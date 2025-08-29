kubectl cp app/kopf_operator.py default/event-handler-f48d85d8d-8rl6f:/app/app/

kubectl cp ./ default/event-handler-6b78d46d47-5bxt6:/app/


docker build -t hiro08081/event_handler:


kopf run app/kopf_operator.py