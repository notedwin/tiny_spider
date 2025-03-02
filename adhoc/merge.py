import aw_client
from aw_transform.filter_period_intersect import _intersecting_eventpairs


def main():
    """
    Inserts all events from one bucket into another bucket, after checking for
    overlap (which you shouldn't have if it was caused by a changing hostname).

    Useful to fix duplicate buckets caused by a changing hostname, as in this issue:
      https://github.com/ActivityWatch/activitywatch/issues/454
    """

    # You need to set testing=False if you're going to run this on your normal instance
    aw = aw_client.ActivityWatchClient()

    buckets = aw.get_buckets()

    dest_id = "aw-watcher-window_notedwin" # ! CHANGE THIS :p
    prefix = dest_id.split("_")[0]
    
    dest_events = aw.get_events(dest_id)

    for id in buckets.keys():
        if id.startswith(prefix) and id != dest_id:
            src_events = aw.get_events(id)
            print(f"Processing bucket {id}...")
            print(f"✓ src events: {len(src_events)}")

            print("Checking overlap...")
            overlaps = list(_intersecting_eventpairs(src_events, dest_events))

            if overlaps:
                print(f"Found {len(overlaps)} overlaps")
                exit(1)

            print("No overlap detected, continuing...")
            print("Inserting source events into destination bucket...")
            aw.insert_events(dest_id, src_events)

            print("Deleting source bucket...")
            aw.delete_bucket(id, force=True)
            print(f"Deleted bucket {id}")

    print("Done!")


if __name__ == "__main__":
    main()
