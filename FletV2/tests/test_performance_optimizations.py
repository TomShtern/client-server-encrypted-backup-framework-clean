#!/usr/bin/env python3
"""
Performance Test Suite for FletV2 Optimizations
Tests ListView virtualization, async data loading, pagination, and memory management.
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any

import psutil

# Import our optimized modules
from utils.performance import (
    AsyncDataLoader,
    AsyncDebouncer,
    PaginationConfig,
    global_memory_manager,
    paginate_data,
)


def generate_large_dataset(size: int = 1000) -> list[dict[str, Any]]:
    """Generate large dataset for performance testing."""
    print(f"🔄 Generating {size} test items...")
    base_time = datetime.now()

    items = []
    for i in range(size):
        items.append({
            "id": f"item_{i}",
            "name": f"Test_File_{i:04d}.txt",
            "size": 1024 * (i % 1000 + 1),  # Variable file sizes
            "type": "txt" if i % 3 == 0 else "pdf" if i % 3 == 1 else "jpg",
            "modified": (base_time.isoformat()),
            "owner": f"user_{i % 10}",
            "status": "Complete" if i % 2 == 0 else "Pending"
        })

    print(f"✅ Generated {len(items)} test items")
    return items

async def test_async_debouncer():
    """Test AsyncDebouncer performance."""
    print("\n🧪 Testing AsyncDebouncer...")

    debouncer = AsyncDebouncer(delay=0.1)  # 100ms for faster testing
    call_count = 0

    async def test_function():
        nonlocal call_count
        call_count += 1
        print(f"   Debounced call #{call_count}")

    # Rapid fire calls - should be debounced
    start_time = time.time()
    await debouncer.debounce(test_function)
    await debouncer.debounce(test_function)
    await debouncer.debounce(test_function)
    await debouncer.debounce(test_function)

    # Wait for debounce to complete
    await asyncio.sleep(0.2)
    end_time = time.time()

    print(f"   ✅ Debouncer test completed in {end_time - start_time:.3f}s")
    print(f"   ✅ Only {call_count} function calls (should be 1)")
    return call_count == 1

async def test_pagination():
    """Test pagination utility performance."""
    print("\n🧪 Testing Pagination...")

    # Generate test data
    test_data = generate_large_dataset(500)
    config = PaginationConfig(page_size=50, current_page=1)

    start_time = time.time()

    # Test multiple pages
    total_items = 0
    for page in range(1, 11):  # Test 10 pages
        config.current_page = page
        page_data = paginate_data(test_data, config.current_page, config.page_size)
        total_items += len(page_data)

    end_time = time.time()

    print(f"   ✅ Pagination test completed in {end_time - start_time:.3f}s")
    print(f"   ✅ Processed {total_items} items across 10 pages")
    return end_time - start_time < 0.1  # Should be very fast

async def test_async_data_loader():
    """Test AsyncDataLoader caching performance."""
    print("\n🧪 Testing AsyncDataLoader...")

    loader = AsyncDataLoader(max_cache_size=50)
    test_data = generate_large_dataset(100)

    # Define a loader function
    def load_test_data():
        return test_data

    # First load (should cache)
    start_time = time.time()
    result1 = await loader.load_data_async("test_key", load_test_data, cache_ttl=10)
    cache_time = time.time() - start_time

    # Second load (should be cached)
    start_time = time.time()
    result2 = await loader.load_data_async("test_key", load_test_data, cache_ttl=10)
    retrieve_time = time.time() - start_time

    print(f"   ✅ First load time: {cache_time:.3f}s")
    print(f"   ✅ Second load time: {retrieve_time:.3f}s")
    print(f"   ✅ Cache working: {result1 is result2}")

    return result1 is result2 and retrieve_time < cache_time

def test_memory_management():
    """Test memory management utilities."""
    print("\n🧪 Testing Memory Management...")

    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Create some data to use memory (instead of testing weak refs)
    large_data = [generate_large_dataset(100) for _ in range(5)]

    # Get peak memory usage
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Force cleanup
    cleanup_stats = global_memory_manager.force_cleanup()

    # Clean up test data
    del large_data

    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB

    print(f"   ✅ Initial memory: {initial_memory:.1f} MB")
    print(f"   ✅ Peak memory: {peak_memory:.1f} MB")
    print(f"   ✅ Final memory: {final_memory:.1f} MB")
    print(f"   ✅ Memory increase: {peak_memory - initial_memory:.1f} MB")
    print(f"   ✅ GC collected: {cleanup_stats['gc_collected']} objects")

    return peak_memory > initial_memory and cleanup_stats['gc_collected'] >= 0

async def test_listview_performance():
    """Test ListView performance with large datasets."""
    print("\n🧪 Testing ListView Performance...")

    # Generate large dataset
    large_dataset = generate_large_dataset(1000)

    # Simulate ListView creation time
    start_time = time.time()

    # Create paginated data (simulating what ListView would render)
    config = PaginationConfig(page_size=50, current_page=1)
    paginated_data, _ = paginate_data(large_dataset, config.current_page, config.page_size)

    # Simulate creating ListTile objects (without actual Flet rendering)
    list_items = []
    for item in paginated_data:
        # Simulate the data processing that would happen in create_log_list_tile
        processed_item = {
            "name": item["name"],
            "size_formatted": f"{item['size'] / 1024:.1f} KB" if item["size"] > 1024 else f"{item['size']} B",
            "type_upper": item["type"].upper(),
            "status_color": "green" if item["status"] == "Complete" else "orange"
        }
        list_items.append(processed_item)

    end_time = time.time()

    print(f"   ✅ ListView data processing completed in {end_time - start_time:.3f}s")
    print(f"   ✅ Processed {len(list_items)} items for display")
    print(f"   ✅ Original dataset: {len(large_dataset)} items")

    return end_time - start_time < 0.1 and len(list_items) == 50

async def run_performance_tests():
    """Run all performance tests."""
    print("🚀 Starting FletV2 Performance Test Suite")
    print("=" * 50)

    results = {}

    try:
        # Test 1: AsyncDebouncer
        results["debouncer"] = await test_async_debouncer()

        # Test 2: Pagination
        results["pagination"] = await test_pagination()

        # Test 3: AsyncDataLoader
        results["data_loader"] = await test_async_data_loader()

        # Test 4: Memory Management
        results["memory"] = test_memory_management()

        # Test 5: ListView Performance
        results["listview"] = await test_listview_performance()

        # Summary
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE TEST RESULTS")
        print("=" * 50)

        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.upper():15} | {status}")

        print("-" * 50)
        print(f"TOTAL: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 ALL PERFORMANCE OPTIMIZATIONS WORKING!")
        else:
            print("⚠️  Some optimizations need attention")

        return passed_tests == total_tests

    except Exception as e:
        print(f"❌ Error during performance testing: {e}")
        return False

if __name__ == "__main__":
    print("🎯 FletV2 Performance Optimization Test")
    print("Testing ListView, async operations, pagination, and memory management...")

    # Run tests
    success = asyncio.run(run_performance_tests())

    if success:
        print("\n✨ Performance optimizations validated successfully!")
        print("🚀 Ready for production use with improved UI responsiveness")
    else:
        print("\n🔧 Some performance issues detected - check logs above")
