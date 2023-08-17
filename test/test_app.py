import unittest
from unittest.mock import patch

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, progress_task, progress_task_class

class TestTasks(unittest.TestCase):
    def test_celery_task(self):
        # 創建一個 Celery 任務並等待完成
        with patch('app.progress_task.update_state') as mock_update_state:
            task = progress_task.apply(args=[5])

            # 驗證 update_state 方法被調用了 5 次
            self.assertEqual(mock_update_state.call_count, 5)


class TestApi(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_start_task_route(self):
        # 發送 POST 請求到 /start_task_post 路由
        response = self.app.post('/celery/start_task_post', json={'input_value': 5})

        # 驗證響應
        self.assertEqual(response.status_code, 200)
        self.assertIn('task_id', response.json)

        # 發送 POST 請求到 /start_task_post 路由
        response = self.app.post('/celery/start_task_post', json={'input_value': 0})

        # 驗證響應
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

        # 發送 GET 請求到 /start_task_get 路由
        response = self.app.get('/celery/start_task_get?input_value=5')

        # 驗證響應
        self.assertEqual(response.status_code, 200)
        self.assertIn('task_id', response.json)

        # 發送 GET 請求到 /start_task_get 路由
        response = self.app.get('/celery/start_task_get?input_value=0')

        # 驗證響應
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_task_progress_route(self):
        with patch.object(progress_task_class, 'update_state') as mock_update_state:
            task = progress_task_class.apply(args=[5])

            # 發送 GET 請求到 /task_progress?<task_id> 路由
            response = self.app.get(f'/celery_result/task_progress?task_id={task.id}')

            # 驗證響應
            self.assertEqual(response.status_code, 200)
            self.assertIn('state', response.json)

            # 驗證 update_state 方法被調用了 5 次
            self.assertEqual(mock_update_state.call_count, 10)

    def test_tasks_route(self):
        # 發送 GET 請求到 /tasks 路由
        response = self.app.get('/celery_result/tasks')

        # 驗證響應
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)

if __name__ == '__main__':
    unittest.main()
    