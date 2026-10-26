def print_summary(total_devices, success_count, failed_count, failed_devices):

    print("\n" + "=" * 60)
    print("NETWORK BACKUP SUMMARY")
    print("=" * 60)

    print(f"Total Devices : {total_devices}")
    print(f"Successful    : {success_count}")
    print(f"Failed        : {failed_count}")

    if failed_devices:

        print("\nFailed Devices")
        print("-" * 60)

        for device in failed_devices:

            print(f"{device['device']}")
            print(f"Error : {device['error']}")
            print("-" * 60)

    print("Backup Process Finished")
    print("=" * 60)