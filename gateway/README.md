# API Gateway
## Development Environment Setup
### Environment Variables
Before running the project, make sure to set up the required environment variables. You should create a `.env` in the root directory of the project.
It should contain the following variables:

```env
BOOKING_SERVICE_URL=http://booking-service:8000
# BOOKING_SERVICE_URL=http://localhost:8090
DESK_INVENTORY_SERVICE_URL=http://desk-inventory-service:8000
# DESK_INVENTORY_SERVICE_URL=http://localhost:8091
USER_SERVICE_URL=http://user-service:8000
# USER_SERVICE_URL=http://localhost:8092
OCCUPANCY_SERVICE_URL=http://occupancy-service:8000
# OCCUPANCY_SERVICE_URL=http://localhost:8093
DESK_INTEGRATION_SERVICE_URL=http://desk-integration-service:8000
# DESK_INTEGRATION_SERVICE_URL=http://localhost:8094
SCHEDULER_SERVICE_URL=http://scheduling-service:8000
# SCHEDULER_SERVICE_URL=http://localhost:8095
```
