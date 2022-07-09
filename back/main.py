from src.app import app
import uvicorn


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True, log_config='configs/logger.yaml')