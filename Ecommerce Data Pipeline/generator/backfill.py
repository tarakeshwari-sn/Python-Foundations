from datetime import datetime, timedelta
from base_generator import EcommerceDataGenerator

def main():
    days = 730
    gen = EcommerceDataGenerator()
    gen._init_base(500, 1000)
    start = datetime.now().date() - timedelta(days=days)
    print(f"Starting {days}-day backfill...")
    for i in range(days):
        dt = start + timedelta(days=i)
        if i % 30 == 0: 
            print(f"Processing {dt}")
        gen.save(gen.generate_day(dt, num_orders=80), dt)
    print("Backfill complete!")

if __name__ == "__main__": 
    main()
