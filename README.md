# BAS
Breach and attack simulation using opensource templates

# Installation
1. Clone repo, clone [uber-common/metta](github.com/uber-common/metta) templates and put them in `app` folder
2. Create venv (optional), install requirements from requirements.txt or pyproject.toml
3. Run Flask app
```
# requirements.txt
pip install -r requirements.txt
# pyproject.toml
python -m pip install .
# Run
flask run
```

# Usage
1. Register and login
2. Create your agents in Agents tab

![Agents creation](https://github.com/user-attachments/assets/c9c4b1a1-3fb8-4bcf-85f1-6ccd48a7bcee)

3. Create your attacks in Attacks tab (click Refresh attacks to load templates)

![Attacks creation](https://github.com/user-attachments/assets/08f48b6f-37d8-4de7-9762-853c2aff52ea)

4. Run your attacks on Agents in Runs tab

![Running attack](https://github.com/user-attachments/assets/14cd00e2-e8de-423e-9f6c-729b6d15107c)

5. View results of a run and dashboard

![Dashboard](https://github.com/user-attachments/assets/2a81c30a-1249-4f2d-bb95-1eccd0bc31fd)
