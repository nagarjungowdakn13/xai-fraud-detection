#!/usr/bin/env python3

import asyncio
import aiohttp
import time
import random
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import statistics

class LoadTester:
    def __init__(self, base_url, concurrent_users=100, test_duration=300):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.test_duration = test_duration
        self.results = {
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'throughput': 0
        }
    
    async def simulate_user(self, user_id):
        """Simulate a single user making requests"""
        session_timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            start_time = time.time()
            
            while time.time() - start_time < self.test_duration:
                # Simulate various user actions
                action = random.choice([
                    self.submit_transaction,
                    self.check_balance,
                    self.view_transaction_history,
                    self.update_profile
                ])
                
                try:
                    await action(session, user_id)
                    self.results['successful_requests'] += 1
                except Exception as e:
                    self.results['failed_requests'] += 1
                    print(f"User {user_id} error: {e}")
                
                # Random delay between actions
                await asyncio.sleep(random.uniform(0.1, 2.0))
    
    async def submit_transaction(self, session, user_id):
        """Submit a transaction for fraud detection"""
        transaction = {
            "user_id": f"user_{user_id}",
            "amount": round(random.uniform(1.0, 5000.0), 2),
            "merchant_id": f"merchant_{random.randint(1, 1000)}",
            "currency": "USD",
            "timestamp": int(time.time() * 1000),
            "location": {
                "ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "country": random.choice(["US", "UK", "CA", "AU", "DE"]),
                "city": random.choice(["New York", "London", "Toronto", "Sydney", "Berlin"])
            },
            "device_fingerprint": f"device_{user_id}",
            "payment_method": random.choice(["credit_card", "debit_card", "paypal"])
        }
        
        start_time = time.time()
        
        async with session.post(
            f"{self.base_url}/api/transactions",
            json=transaction,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            
            return await response.json()
    
    async def check_balance(self, session, user_id):
        """Check user balance"""
        start_time = time.time()
        
        async with session.get(
            f"{self.base_url}/api/users/{user_id}/balance"
        ) as response:
            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
    
    async def view_transaction_history(self, session, user_id):
        """View transaction history"""
        start_time = time.time()
        
        async with session.get(
            f"{self.base_url}/api/users/{user_id}/transactions"
        ) as response:
            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
    
    async def update_profile(self, session, user_id):
        """Update user profile"""
        start_time = time.time()
        
        profile_update = {
            "email": f"user{user_id}@test.com",
            "phone": f"+1{random.randint(1000000000, 9999999999)}"
        }
        
        async with session.put(
            f"{self.base_url}/api/users/{user_id}/profile",
            json=profile_update
        ) as response:
            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
    
    async def run_load_test(self):
        """Run the complete load test"""
        print(f"Starting load test with {self.concurrent_users} concurrent users")
        print(f"Test duration: {self.test_duration} seconds")
        print("=" * 50)
        
        start_time = time.time()
        
        # Create tasks for all concurrent users
        tasks = [
            self.simulate_user(user_id)
            for user_id in range(self.concurrent_users)
        ]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        self.results['throughput'] = self.results['successful_requests'] / total_time
        
        self.print_results()
    
    def print_results(self):
        """Print load test results"""
        print("\n" + "=" * 50)
        print("LOAD TEST RESULTS")
        print("=" * 50)
        
        total_requests = self.results['successful_requests'] + self.results['failed_requests']
        success_rate = (self.results['successful_requests'] / total_requests) * 100
        
        print(f"Total Requests: {total_requests:,}")
        print(f"Successful: {self.results['successful_requests']:,}")
        print(f"Failed: {self.results['failed_requests']:,}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Throughput: {self.results['throughput']:.2f} requests/second")
        
        if self.results['response_times']:
            print(f"Average Response Time: {statistics.mean(self.results['response_times']):.3f}s")
            print(f"95th Percentile: {np.percentile(self.results['response_times'], 95):.3f}s")
            print(f"Max Response Time: {max(self.results['response_times']):.3f}s")
        
        print("=" * 50)

async def main():
    # Configuration
    BASE_URL = "http://your-production-domain.com"
    CONCURRENT_USERS = 500  # Simulate 500 concurrent users
    TEST_DURATION = 600     # 10 minutes
    
    tester = LoadTester(BASE_URL, CONCURRENT_USERS, TEST_DURATION)
    await tester.run_load_test()

if __name__ == "__main__":
    asyncio.run(main())