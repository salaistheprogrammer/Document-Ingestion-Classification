# Document-Ingestion-Classification
**The development of this project is underway, the integration of routing agents, AWS textract and the fine-tuned LayoutLMv3 model is yet to be done:**
  1. The extraction logic used in the "approach_two.py" file tries to mimic the way the AWS textract processes documents and gives outputs (texts and the corresponding bounding boxes), this was done for testing purposes.
  2. Additionally, the fine-tuning of the LayoutLMv3 is underway too, based on how feasible and accurate it is, the decision to use it in the classifier agent will be taken. Other wise an external service may be used.
  3. The routing agents are completely understood and can be implemented anytime, there are already examples to the implementation of it.

**Some files are not given in this repository**:
  1. Files such as "credentials.json" and "token.json" are not given in this repository for security purposes. these files are required to authenticate a third-party-app to let it access an account ex. Drive and Gmail.
