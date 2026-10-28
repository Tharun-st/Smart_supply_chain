"""
Test Flask Page Routes and API Endpoints
Verifies that all pages render with status 200 and all core APIs respond properly.
"""

import unittest
from app import create_app

class TestAppRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_pages_render_200(self):
        pages = [
            "/",
            "/dashboard",
            "/login",
            "/products",
            "/suppliers",
            "/inventory",
            "/orders",
            "/warehouses",
            "/deliveries",
            "/dsa-operations",
            "/search-sort",
            "/optimization",
            "/database-ops",
            "/ds/linked-list",
            "/ds/stack",
            "/ds/queue",
            "/ds/binary-tree",
            "/ds/bst",
            "/ds/graph",
            "/algorithms/searching",
            "/algorithms/sorting",
            "/algorithms/bfs-dfs",
            "/algorithms/complexity",
            "/analytics",
            "/reports",
            "/activity-log",
            "/settings",
            "/overview"
        ]
        for url in pages:
            with self.subTest(url=url):
                res = self.client.get(url)
                self.assertEqual(res.status_code, 200, f"Page {url} failed with status {res.status_code}")

    def test_api_endpoints(self):
        # 1. Dashboard stats
        res = self.client.get("/api/dashboard/stats")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data["status"], "success")

        # 2. Analytics telemetry
        res = self.client.get("/api/analytics")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # 3. System status
        res = self.client.get("/api/system/status")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # 4. Reports data
        for r_type in ["products", "suppliers", "inventory", "orders", "deliveries", "algorithms", "optimization"]:
            res = self.client.get(f"/api/reports/{r_type}")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json()["status"], "success")

        # 5. Algorithm logs
        res = self.client.get("/api/algorithms/logs")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # 6. Complexity table
        res = self.client.get("/api/algorithms/complexity/table")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # 7. Demo run API
        res = self.client.post("/api/demo/run")
        self.assertEqual(res.status_code, 200)
        demo_json = res.get_json()
        self.assertEqual(demo_json["status"], "success")
        self.assertEqual(demo_json["total_steps"], 21)

if __name__ == "__main__":
    unittest.main()
