# eval_engine.py
import json
import os

def run_benchmark(test_data_path="test_db.json", sample_size=50):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(BASE_DIR, test_data_path)
    
    with open(full_path, "r") as f:
        test_cases = json.load(f)[:sample_size]
        
    tp = fp = tn = fn = 0
    REPRESENTMENT_FEE = 1500.0  # ₹1500 bank fee per dispute
    results = []
    
    for case in test_cases:
        ground_truth = case["ground_truth"]
        amount = case["disputed_amount"]
        
        # Rule prediction logic that handles clear cases + edge cases
        avs_ok = case.get("avs_match") in ["MATCH", "PASS"]
        cvc_ok = case.get("cvc_match") == "PASS"
        delivered = case.get("delivery_status") == "Delivered"
        short_distance = case.get("ip_distance_km", 999) < 100
        
        # System decides to FIGHT if AVS/CVC pass and item was delivered locally
        if (avs_ok or cvc_ok) and delivered and short_distance:
            prediction = "FIGHT"
        else:
            prediction = "ACCEPT"
        
        # Calculate Confusion Matrix
        if prediction == "FIGHT" and ground_truth == "FIGHT":
            tp += 1
            status = "True Positive (Success)"
        elif prediction == "FIGHT" and ground_truth == "ACCEPT":
            fp += 1
            status = "False Positive (Fee Wasted)"
        elif prediction == "ACCEPT" and ground_truth == "ACCEPT":
            tn += 1
            status = "True Negative (Fee Saved)"
        else:
            fn += 1
            status = "False Negative (Revenue Missed)"
            
        results.append({
            "Dispute ID": case["dispute_id"],
            "Ground Truth": ground_truth,
            "Prediction": prediction,
            "Amount": f"₹{amount:,.2f}",
            "Result": status
        })
        
    total_eval = len(test_cases)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    accuracy = (tp + tn) / total_eval if total_eval > 0 else 0.0
    
    # Financial Impact Math
    # Naive baseline fights 100% of disputes (paying fees even on true fraud)
    total_true_fraud = sum(1 for c in test_cases if c["ground_truth"] == "ACCEPT")
    naive_fpc = total_true_fraud * REPRESENTMENT_FEE
    
    # Our model's false positive cost
    model_fpc = fp * REPRESENTMENT_FEE
    cost_savings = naive_fpc - model_fpc
    
    return {
        "precision": round(precision * 100, 1),
        "recall": round(recall * 100, 1),
        "accuracy": round(accuracy * 100, 1),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "total_cases": total_eval,
        "model_fpc": model_fpc,
        "cost_savings": cost_savings,
        "results_table": results
    }