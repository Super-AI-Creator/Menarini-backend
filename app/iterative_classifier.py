
def iterative_classification(subject, body, classifier):
    try:
        subject_result = classifier(subject)[0]
        if subject_result["label"] == "POSITIVE" and subject_result["score"] > 0.8:
            return "PO", subject_result["score"]
        elif subject_result["score"] > 0.4:
            body_result = classifier(body)[0]
            if body_result["label"] == "POSITIVE":
                return "PO", body_result["score"]
            return "Not PO", body_result["score"]
        return "Not PO", subject_result["score"]
    except Exception as e:
        return "Error", 0.0