# if running test_inifical runs without errors, then run the create function
uv run test_infisical.py
uv run python3 -c "from screentime import create; create()"
uv run evidence/evidence.py