from database import (
    get_all_appointments,
    get_all_emails,
    get_all_email_processing,
    get_basic_manual_pending,
    get_nonbusiness_unreviewed,
    get_priority_unreviewed,
)
from utils.color import Logger
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

class EmailsAnalysis(Logger):
    name: str = "EmailsAnalysis"
    color: str = Logger.SKY_BLUE

    def get_volume_entered_vs_processed(self):
        """Metric 1: Total emails entered vs processed"""
        emails = get_all_emails()
        processed = get_all_email_processing()
        
        self.log(f"Emails entered: {len(emails)}")
        self.log(f"Emails processed: {len(processed)}")
        self.log(f"Unprocessed: {len(emails) - len(processed)}")
        
        return {
            "entered": len(emails),
            "processed": len(processed),
            "unprocessed": len(emails) - len(processed)
        }

    def get_classification_breakdown(self):
        """Metric 2: Classification volume breakdown (BASIC, PRIORITY, NON_BUSINESS)"""
        processed = get_all_email_processing()
        
        counts = {"BASIC": 0, "PRIORITY": 0, "NON_BUSINESS": 0}
        unknown = 0
        
        for record in processed:
            classification = record.get("classification")
            if classification in counts:
                counts[classification] += 1
            elif classification:
                unknown += 1
        
        total = sum(counts.values()) + unknown
        if total > 0:
            self.log(f"BASIC: {counts['BASIC']} ({counts['BASIC']/total*100:.1f}%)")
            self.log(f"PRIORITY: {counts['PRIORITY']} ({counts['PRIORITY']/total*100:.1f}%)")
            self.log(f"NON_BUSINESS: {counts['NON_BUSINESS']} ({counts['NON_BUSINESS']/total*100:.1f}%)")
            if unknown:
                self.log(f"Unknown: {unknown}")
        else:
            self.log("No processed emails found")
        
        return {
            "counts": counts,
            "unknown": unknown,
            "total": total,
            "percentages": {k: (v/total*100) for k, v in counts.items()} if total > 0 else {}
        }

    def get_top_senders_by_volume(self):
        """Metric 3: All senders ranked by volume (full dataset)"""
        emails = get_all_emails()
        
        sender_counts = {}
        for email in emails:
            sender = email.get("sender_email")
            name = email.get("sender_name", sender)
            if sender not in sender_counts:
                sender_counts[sender] = {
                    "count": 0,
                    "name": name,
                    "email": sender
                }
            sender_counts[sender]["count"] += 1
        
        # Sort by volume descending
        sorted_senders = sorted(sender_counts.values(), key=lambda x: x["count"], reverse=True)
        
        self.log(f"Total unique senders: {len(sorted_senders)}")
        self.log("\nTop 10 senders by volume:")
        for i, sender in enumerate(sorted_senders[:10], 1):
            self.log(f"  {i}. {sender['name']} ({sender['email']}): {sender['count']} emails")
        
        return {
            "total_unique_senders": len(sorted_senders),
            "all_senders": sorted_senders,
            "top_10": sorted_senders[:10]
        }

    def get_top_senders_by_classification(self):
        """Metric 4: For each sender, their classification distribution"""
        processed = get_all_email_processing()
        
        sender_data = {}
        for record in processed:
            sender = record.get("sender_email")
            classification = record.get("classification")
            
            if sender not in sender_data:
                sender_data[sender] = {
                    "total": 0,
                    "classifications": {"BASIC": 0, "PRIORITY": 0, "NON_BUSINESS": 0}
                }
            
            sender_data[sender]["total"] += 1
            if classification in sender_data[sender]["classifications"]:
                sender_data[sender]["classifications"][classification] += 1
        
        # Add dominant classification and percentage
        for sender, data in sender_data.items():
            classes = data["classifications"]
            dominant = max(classes, key=classes.get)
            data["dominant_classification"] = dominant
            data["dominant_percentage"] = (classes[dominant] / data["total"]) * 100 if data["total"] > 0 else 0
        
        # Sort by total volume
        sorted_senders = sorted(sender_data.items(), key=lambda x: x[1]["total"], reverse=True)
        
        self.log(f"Total unique senders in processed emails: {len(sorted_senders)}")
        self.log("\nTop 10 senders by classification distribution:")
        for i, (sender, data) in enumerate(sorted_senders[:10], 1):
            classes = data["classifications"]
            self.log(f"  {i}. {sender} ({data['total']} emails)")
            self.log(f"     Dominant: {data['dominant_classification']} ({data['dominant_percentage']:.0f}%)")
            self.log(f"     B:{classes['BASIC']} P:{classes['PRIORITY']} NB:{classes['NON_BUSINESS']}")
        
        return {
            "senders": dict(sorted_senders),
            "total_senders": len(sorted_senders)
        }

    def get_nonbusiness_top_type_and_sender(self):
        """Metric 5: Most common nonbusiness type AND who sent it most"""
        nonbusiness = get_nonbusiness_unreviewed()
        
        if not nonbusiness:
            self.log("No non-business emails found")
            return {"top_type": None, "top_sender": None, "type_count": 0}
        
        # Rich data collection
        type_counts = {}
        sender_counts = {}
        sender_by_type = {}
        
        for record in nonbusiness:
            nb_type = record.get("nonbusiness_type")
            sender = record.get("sender_email")
            sender_name = record.get("sender_name", sender)
            
            # Type counts
            type_counts[nb_type] = type_counts.get(nb_type, 0) + 1
            
            # Sender counts
            if sender not in sender_counts:
                sender_counts[sender] = {"count": 0, "name": sender_name, "types": {}}
            sender_counts[sender]["count"] += 1
            sender_counts[sender]["types"][nb_type] = sender_counts[sender]["types"].get(nb_type, 0) + 1
            
            # Sender by type (for top sender per type)
            if nb_type not in sender_by_type:
                sender_by_type[nb_type] = {}
            sender_by_type[nb_type][sender] = sender_by_type[nb_type].get(sender, 0) + 1
        
        # Most common type
        top_type = max(type_counts, key=type_counts.get)
        top_type_count = type_counts[top_type]
        
        # Who sent that type the most
        top_sender_for_type = max(sender_by_type[top_type], key=sender_by_type[top_type].get) if top_type in sender_by_type else None
        top_sender_count = sender_by_type.get(top_type, {}).get(top_sender_for_type, 0)
        top_sender_name = sender_counts.get(top_sender_for_type, {}).get("name", top_sender_for_type)
        
        # Who sends the most non-business overall
        top_overall_sender = max(sender_counts.items(), key=lambda x: x[1]["count"])
        top_overall_sender_name = top_overall_sender[1]["name"]
        top_overall_sender_email = top_overall_sender[0]
        
        self.log(f"Total non-business emails: {len(nonbusiness)}")
        self.log(f"Unique non-business senders: {len(sender_counts)}")
        self.log(f"\nMost common non-business type: '{top_type}' ({top_type_count} emails, {top_type_count/len(nonbusiness)*100:.1f}%)")
        self.log(f"Top sender of '{top_type}': {top_sender_name} ({top_sender_for_type}) - {top_sender_count} emails")
        self.log(f"\nTop non-business sender overall: {top_overall_sender_name} ({top_overall_sender_email}) - {top_overall_sender[1]['count']} emails")
        
        # Show all type distributions
        self.log("\nNon-business type distribution:")
        for nb_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            self.log(f"  {nb_type}: {count} ({count/len(nonbusiness)*100:.1f}%)")
        
        return {
            "total_nonbusiness": len(nonbusiness),
            "unique_senders": len(sender_counts),
            "top_type": top_type,
            "top_type_count": top_type_count,
            "top_type_percentage": round(top_type_count/len(nonbusiness)*100, 2),
            "top_sender_of_top_type": {
                "email": top_sender_for_type,
                "name": top_sender_name,
                "count": top_sender_count
            },
            "top_overall_sender": {
                "email": top_overall_sender_email,
                "name": top_overall_sender_name,
                "count": top_overall_sender[1]["count"]
            },
            "type_distribution": type_counts,
            "sender_distribution": {k: v["count"] for k, v in sender_counts.items()}
        }

    def get_priority_top_type_and_sender(self):
        """Metric 6: Most common priority type AND who sent it most"""
        priority = get_priority_unreviewed()
        
        if not priority:
            self.log("No priority emails found")
            return {"top_type": None, "top_sender": None, "type_count": 0}
        
        type_counts = {}
        sender_counts = {}
        sender_by_type = {}
        confidence_by_type = {}
        
        for record in priority:
            priority_type = record.get("priority_type")
            sender = record.get("sender_email")
            sender_name = record.get("sender_name", sender)
            confidence = record.get("confidence")
            
            # Type counts
            type_counts[priority_type] = type_counts.get(priority_type, 0) + 1
            
            # Confidence by type
            if priority_type not in confidence_by_type:
                confidence_by_type[priority_type] = []
            confidence_by_type[priority_type].append(confidence)
            
            # Sender counts
            if sender not in sender_counts:
                sender_counts[sender] = {"count": 0, "name": sender_name, "types": {}}
            sender_counts[sender]["count"] += 1
            sender_counts[sender]["types"][priority_type] = sender_counts[sender]["types"].get(priority_type, 0) + 1
            
            # Sender by type
            if priority_type not in sender_by_type:
                sender_by_type[priority_type] = {}
            sender_by_type[priority_type][sender] = sender_by_type[priority_type].get(sender, 0) + 1
        
        # Most common type
        top_type = max(type_counts, key=type_counts.get)
        top_type_count = type_counts[top_type]
        
        # Average confidence for top type
        avg_confidence = sum(confidence_by_type[top_type]) / len(confidence_by_type[top_type]) if confidence_by_type[top_type] else 0
        
        # Who sent that type the most
        top_sender_for_type = max(sender_by_type[top_type], key=sender_by_type[top_type].get) if top_type in sender_by_type else None
        top_sender_count = sender_by_type.get(top_type, {}).get(top_sender_for_type, 0)
        top_sender_name = sender_counts.get(top_sender_for_type, {}).get("name", top_sender_for_type)
        
        # Who sends the most priority overall
        top_overall_sender = max(sender_counts.items(), key=lambda x: x[1]["count"])
        top_overall_sender_name = top_overall_sender[1]["name"]
        top_overall_sender_email = top_overall_sender[0]
        
        self.log(f"Total priority emails: {len(priority)}")
        self.log(f"Unique priority senders: {len(sender_counts)}")
        self.log(f"\nMost common priority type: '{top_type}' ({top_type_count} emails, {top_type_count/len(priority)*100:.1f}%)")
        self.log(f"Average confidence for '{top_type}': {avg_confidence:.2f}")
        self.log(f"Top sender of '{top_type}': {top_sender_name} ({top_sender_for_type}) - {top_sender_count} emails")
        self.log(f"\nTop priority sender overall: {top_overall_sender_name} ({top_overall_sender_email}) - {top_overall_sender[1]['count']} emails")
        
        # Show all type distributions
        self.log("\nPriority type distribution:")
        for p_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            avg_conf = sum(confidence_by_type[p_type]) / len(confidence_by_type[p_type]) if confidence_by_type[p_type] else 0
            self.log(f"  {p_type}: {count} ({count/len(priority)*100:.1f}%) [avg confidence: {avg_conf:.2f}]")
        
        return {
            "total_priority": len(priority),
            "unique_senders": len(sender_counts),
            "top_type": top_type,
            "top_type_count": top_type_count,
            "top_type_percentage": round(top_type_count/len(priority)*100, 2),
            "top_type_avg_confidence": round(avg_confidence, 2),
            "top_sender_of_top_type": {
                "email": top_sender_for_type,
                "name": top_sender_name,
                "count": top_sender_count
            },
            "top_overall_sender": {
                "email": top_overall_sender_email,
                "name": top_overall_sender_name,
                "count": top_overall_sender[1]["count"]
            },
            "type_distribution": type_counts,
            "confidence_by_type": {k: round(sum(v)/len(v), 2) for k, v in confidence_by_type.items()}
        }

    def get_automation_success_rate(self):
        """Metric 7: Automation success rate with breakdown by classification"""
        processed = get_all_email_processing()
        
        if not processed:
            self.log("No processed emails found")
            return {"success_rate": 0, "successful": 0, "failed": 0, "total": 0}
        
        total = len(processed)
        successful = sum(1 for record in processed if record.get("success"))
        failed = total - successful
        success_rate = (successful / total) * 100 if total else 0
        
        # Breakdown by classification
        by_classification = {"BASIC": {"total": 0, "successful": 0}, 
                            "PRIORITY": {"total": 0, "successful": 0}, 
                            "NON_BUSINESS": {"total": 0, "successful": 0}}
        
        for record in processed:
            classification = record.get("classification")
            is_success = record.get("success")
            
            if classification in by_classification:
                by_classification[classification]["total"] += 1
                if is_success:
                    by_classification[classification]["successful"] += 1
        
        self.log(f"Total processed: {total}")
        self.log(f"Successful: {successful}")
        self.log(f"Failed: {failed}")
        self.log(f"Overall success rate: {success_rate:.1f}%")
        self.log("\nSuccess rate by classification:")
        for class_type, data in by_classification.items():
            if data["total"] > 0:
                rate = (data["successful"] / data["total"]) * 100
                self.log(f"  {class_type}: {data['successful']}/{data['total']} ({rate:.1f}%)")
            else:
                self.log(f"  {class_type}: No data")
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "by_classification": {
                class_type: {
                    "total": data["total"],
                    "successful": data["successful"],
                    "rate": round((data["successful"] / data["total"]) * 100, 2) if data["total"] > 0 else 0
                }
                for class_type, data in by_classification.items()
            }
        }

    def get_total_appointments_count(self):
        """Metric 8: Total appointments scheduled with status breakdown"""
        appointments = get_all_appointments()
        
        if not appointments:
            self.log("No appointments found")
            return {"total": 0}
        
        calendar_status_counts = {}
        confirmation_status_counts = {}
        
        for appt in appointments:
            cal_status = appt.get("calendar_status")
            conf_status = appt.get("confirmation_email_status")
            
            calendar_status_counts[cal_status] = calendar_status_counts.get(cal_status, 0) + 1
            confirmation_status_counts[conf_status] = confirmation_status_counts.get(conf_status, 0) + 1
        
        total = len(appointments)
        self.log(f"Total appointments scheduled: {total}")
        self.log("\nCalendar status breakdown:")
        for status, count in calendar_status_counts.items():
            self.log(f"  {status}: {count} ({count/total*100:.1f}%)")
        self.log("\nConfirmation email status:")
        for status, count in confirmation_status_counts.items():
            self.log(f"  {status}: {count} ({count/total*100:.1f}%)")
        
        return {
            "total": total,
            "calendar_status": calendar_status_counts,
            "confirmation_status": confirmation_status_counts
        }

    def get_pending_manual_replies_count(self):
        """Metric 9: Pending manual replies with failure reason breakdown"""
        pending = get_basic_manual_pending()
        
        if not pending:
            self.log("No pending manual replies")
            return {"total": 0, "failure_reasons": {}, "rag_statuses": {}}
        
        failure_reasons = {}
        rag_statuses = {}
        
        for record in pending:
            reason = record.get("failure_reason", "Unknown")
            rag_status = record.get("rag_status", "Unknown")
            
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            rag_statuses[rag_status] = rag_statuses.get(rag_status, 0) + 1
        
        total = len(pending)
        self.log(f"Total pending manual replies: {total}")
        self.log("\nFailure reasons breakdown:")
        for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True):
            self.log(f"  {reason}: {count} ({count/total*100:.1f}%)")
        self.log("\nRAG status breakdown:")
        for status, count in rag_statuses.items():
            self.log(f"  {status}: {count} ({count/total*100:.1f}%)")
        
        return {
            "total": total,
            "failure_reasons": failure_reasons,
            "rag_statuses": rag_statuses
        }

    def get_most_failed_classification(self):
        """Metric 10: Which classification type fails the most (by count and rate)"""
        processed = get_all_email_processing()
        
        if not processed:
            self.log("No processed emails found")
            return {"most_failed_by_count": None, "most_failed_by_rate": None, "classification_stats": {}}
        
        classification_stats = {"BASIC": {"total": 0, "failed": 0}, 
                               "PRIORITY": {"total": 0, "failed": 0}, 
                               "NON_BUSINESS": {"total": 0, "failed": 0}}
        
        for record in processed:
            classification = record.get("classification")
            success = record.get("success")
            
            if classification in classification_stats:
                classification_stats[classification]["total"] += 1
                if not success:
                    classification_stats[classification]["failed"] += 1
        
        # Calculate rates
        for class_type, stats in classification_stats.items():
            if stats["total"] > 0:
                stats["rate"] = (stats["failed"] / stats["total"]) * 100
            else:
                stats["rate"] = 0
        
        # Find most failed by count and by rate
        most_failed_by_count = max(classification_stats.items(), key=lambda x: x[1]["failed"]) if any(s["failed"] for s in classification_stats.values()) else (None, None)
        most_failed_by_rate = max(classification_stats.items(), key=lambda x: x[1]["rate"]) if any(s["total"] for s in classification_stats.values()) else (None, None)
        
        self.log("Failure analysis by classification:")
        for class_type, stats in classification_stats.items():
            if stats["total"] > 0:
                self.log(f"  {class_type}: {stats['failed']}/{stats['total']} fails ({stats['rate']:.1f}%)")
            else:
                self.log(f"  {class_type}: No data")
        
        if most_failed_by_count[0]:
            self.log(f"\nMost failed by volume: {most_failed_by_count[0]} ({most_failed_by_count[1]['failed']} fails)")
        if most_failed_by_rate[0]:
            self.log(f"Most failed by rate: {most_failed_by_rate[0]} ({most_failed_by_rate[1]['rate']:.1f}% failure rate)")
        
        return {
            "most_failed_by_count": {"classification": most_failed_by_count[0], "failed_count": most_failed_by_count[1]["failed"] if most_failed_by_count[1] else 0},
            "most_failed_by_rate": {"classification": most_failed_by_rate[0], "failure_rate": round(most_failed_by_rate[1]["rate"], 2) if most_failed_by_rate[1] else 0},
            "classification_stats": classification_stats
        }

    def run_all_analysis(self):
        """Run all 10 metrics and return combined results"""
        self.log("=" * 60)
        self.log("EMAIL ANALYSIS DASHBOARD")
        self.log("=" * 60)
        
        results = {
            "metric_1_entered_vs_processed": self.get_volume_entered_vs_processed(),
            "metric_2_classification_breakdown": self.get_classification_breakdown(),
            "metric_3_top_senders_by_volume": self.get_top_senders_by_volume(),
            "metric_4_top_senders_by_classification": self.get_top_senders_by_classification(),
            "metric_5_nonbusiness_top_type_and_sender": self.get_nonbusiness_top_type_and_sender(),
            "metric_6_priority_top_type_and_sender": self.get_priority_top_type_and_sender(),
            "metric_7_automation_success_rate": self.get_automation_success_rate(),
            "metric_8_total_appointments": self.get_total_appointments_count(),
            "metric_9_pending_manual_replies": self.get_pending_manual_replies_count(),
            "metric_10_most_failed_classification": self.get_most_failed_classification()
        }
        
        self.log("\n" + "=" * 60)
        self.log("ANALYSIS COMPLETE")
        self.log("=" * 60)
        
        return results


if __name__ == "__main__":
    
    analysis = EmailsAnalysis()
    results = analysis.run_all_analysis()
    
    print("\n" + "=" * 80)
    print("📊 FINAL DASHBOARD SUMMARY")
    print("=" * 80)
    
    # Metric 1
    m1 = results["metric_1_entered_vs_processed"]
    print(f"\n📬 VOLUME: {m1['entered']} entered | {m1['processed']} processed | {m1['unprocessed']} unprocessed")
    
    # Metric 2
    m2 = results["metric_2_classification_breakdown"]
    if m2['total'] > 0:
        print("\n🏷️ CLASSIFICATIONS:")
        for class_type, count in m2['counts'].items():
            if count > 0:
                print(f"   {class_type}: {count} ({m2['percentages'][class_type]:.1f}%)")
        if m2['unknown'] > 0:
            print(f"   UNKNOWN: {m2['unknown']}")
    
    # Metric 3
    m3 = results["metric_3_top_senders_by_volume"]
    print("\n👤 TOP 5 SENDERS BY VOLUME:")
    for i, sender in enumerate(m3['top_10'][:5], 1):
        print(f"   {i}. {sender['name']}: {sender['count']} emails")
    
    # Metric 4
    m4 = results["metric_4_top_senders_by_classification"]
    print("\n🎯 TOP 5 SENDERS BY CLASSIFICATION:")
    for i, (sender, data) in enumerate(list(m4['senders'].items())[:5], 1):
        classes = data['classifications']
        print(f"   {i}. {sender}: {data['total']} emails (Dom: {data['dominant_classification']})")
    
    # Metric 5
    m5 = results["metric_5_nonbusiness_top_type_and_sender"]
    if m5['top_type']:
        print("\n📧 NON-BUSINESS:")
        print(f"   Most common type: {m5['top_type']} ({m5['top_type_count']} emails, {m5['top_type_percentage']}%)")
        print(f"   Top sender of this type: {m5['top_sender_of_top_type']['name']} ({m5['top_sender_of_top_type']['count']} emails)")
    
    # Metric 6
    m6 = results["metric_6_priority_top_type_and_sender"]
    if m6['top_type']:
        print("\n⚠️ PRIORITY:")
        print(f"   Most common type: {m6['top_type']} ({m6['top_type_count']} emails, {m6['top_type_percentage']}%)")
        print(f"   Avg confidence: {m6['top_type_avg_confidence']}")
        print(f"   Top sender: {m6['top_sender_of_top_type']['name']} ({m6['top_sender_of_top_type']['count']} emails)")
    
    # Metric 7
    m7 = results["metric_7_automation_success_rate"]
    print("\n🤖 AUTOMATION:")
    print(f"   Success rate: {m7['success_rate']}% ({m7['successful']}/{m7['total']})")
    for class_type, data in m7['by_classification'].items():
        if data['total'] > 0:
            print(f"   {class_type}: {data['rate']}% ({data['successful']}/{data['total']})")
    
    # Metric 8
    m8 = results["metric_8_total_appointments"]
    print(f"\n📅 APPOINTMENTS: {m8['total']} total")
    if m8['total'] > 0:
        print(f"   Calendar: {m8['calendar_status']}")
        print(f"   Confirmations: {m8['confirmation_status']}")
    
    # Metric 9
    m9 = results["metric_9_pending_manual_replies"]
    print(f"\n⏳ PENDING MANUAL: {m9['total']}")
    
    # Metric 10
    m10 = results["metric_10_most_failed_classification"]
    if m10['most_failed_by_count']['classification']:
        print("\n💥 MOST FAILED:")
        print(f"   By volume: {m10['most_failed_by_count']['classification']} ({m10['most_failed_by_count']['failed_count']} fails)")
        print(f"   By rate: {m10['most_failed_by_rate']['classification']} ({m10['most_failed_by_rate']['failure_rate']}%)")
    
    print("\n" + "=" * 80)