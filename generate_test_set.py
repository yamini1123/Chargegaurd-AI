# generate_test_set.py
import json
import random

def generate_realistic_test_cases():
    test_cases = []
    
    # 1. Winnable Friendly Fraud Cases (22)
    for i in range(1, 23):
        test_cases.append({
            "dispute_id": f"TEST_DP_{100 + i}",
            "order_id": f"ORD_TEST_{1000 + i}",
            "disputed_amount": round(random.uniform(2000, 20000), 2),
            "avs_match": "MATCH",
            "cvc_match": "PASS",
            "ip_distance_km": round(random.uniform(0.5, 3.0), 1),
            "delivery_status": "Delivered",
            "chat_history": "Customer acknowledged receiving product in chat.",
            "ground_truth": "FIGHT"
        })
        
    # 2. Unwinnable True Fraud Cases (23)
    for i in range(23, 46):
        test_cases.append({
            "dispute_id": f"TEST_DP_{100 + i}",
            "order_id": f"ORD_TEST_{1000 + i}",
            "disputed_amount": round(random.uniform(10000, 50000), 2),
            "avs_match": "FAIL",
            "cvc_match": "FAIL",
            "ip_distance_km": round(random.uniform(3000.0, 9000.0), 1),
            "delivery_status": "Failed / In Transit",
            "chat_history": "None",
            "ground_truth": "ACCEPT"
        })

    # 3. Tricky Edge Cases (5) - Creates realistic FP / FN errors
    for i in range(46, 51):
        if i % 2 == 0:
            # VPN User (Looks like fraud due to long distance, but is winnable) -> Generates FN
            test_cases.append({
                "dispute_id": f"TEST_DP_{100 + i}",
                "order_id": f"ORD_TEST_{1000 + i}",
                "disputed_amount": round(random.uniform(5000, 15000), 2),
                "avs_match": "MATCH",
                "cvc_match": "PASS",
                "ip_distance_km": 1500.0,
                "delivery_status": "Delivered",
                "chat_history": "Customer asked about warranty after delivery.",
                "ground_truth": "FIGHT"
            })
        else:
            # Stolen package claim (Delivered locally, but ground truth is unwinnable) -> Generates FP
            test_cases.append({
                "dispute_id": f"TEST_DP_{100 + i}",
                "order_id": f"ORD_TEST_{1000 + i}",
                "disputed_amount": round(random.uniform(8000, 25000), 2),
                "avs_match": "MATCH",
                "cvc_match": "PASS",
                "ip_distance_km": 5.0,
                "delivery_status": "Delivered",
                "chat_history": "Porch theft reported to police.",
                "ground_truth": "ACCEPT"
            })

    # Shuffle cases so ground truths are randomly distributed
    random.seed(42) # Fixed seed for reproducible metrics
    random.shuffle(test_cases)

    with open("test_db.json", "w") as f:
        json.dump(test_cases, f, indent=2)
        
    print("✅ Successfully generated test_db.json with 50 shuffled cases.")

if __name__ == "__main__":
    generate_realistic_test_cases()