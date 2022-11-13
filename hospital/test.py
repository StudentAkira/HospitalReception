from datetime import datetime, timedelta

now = datetime.now().replace(second=0, microsecond=0)
now += timedelta(minutes=(30 - now.minute % 30))
print(now)

tickets_times = [now + timedelta(minutes=30*minutes_step, days=day_step)
                 for minutes_step in
                 range(20) for day_step in range(30) if (now + timedelta(minutes=30*minutes_step, days=day_step)).hour < 19]

for i in tickets_times:
    print(i)
