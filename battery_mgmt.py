import os
import sys
import time
import psutil
import notif_window

# Change working dir to script's home directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_threshold_reached(lthresh = 30, uthresh = 95):
    global g_lthresh, g_uthresh

    if g_lthresh is not None:
        lthresh = g_lthresh

    if g_uthresh is not None:
        uthresh = g_uthresh

    battery = psutil.sensors_battery()

    bper = battery.percent
    bplugged = battery.power_plugged

    result = {'status': 0, 'msg': 'I\'m still holding on'}

    if (bper < lthresh) and not bplugged:
        result['msg'] = f'Battery Low ({bper}%)'
        result['status'] = -1

    elif (bper > uthresh) and bplugged:
        result['msg'] = f'Battery Maxed ({bper}%)'
        result['status'] = 1

    return result

def main():
    notification_snooze_seconds = 20
    last_notif_epoch = None

    while True:
        try:
            tr = check_threshold_reached()
            if tr['status'] == -1:
                notify = 0
                if last_notif_epoch is None:
                    notify = 1

                elif time.time() >= last_notif_epoch + notification_snooze_seconds:
                    notify = 1

                if notify:
                    status_time = time.time()
                    last_notif_epoch = time.time()
                    notif_window.show_alert(tr.get('msg'), "Plug in your charger")
                    # break

            if tr['status'] == 1:
                notify = 0
                if last_notif_epoch is None:
                    notify = 1

                elif time.time() >= last_notif_epoch + notification_snooze_seconds:
                    notify = 1

                if notify:
                    status_time = time.time()
                    last_notif_epoch = time.time()
                    notif_window.show_alert(tr.get('msg'), "Remove your charger")
                    # break

        except KeyboardInterrupt:
            print("Battery Management Aborted...")
            break
        except Exception:
            raise
            pass

if __name__ == "__main__":
    global g_lthresh, g_uthresh

    g_lthresh, g_uthresh = None, None

    if len(sys.argv) == 3:
        if all(i.isnumeric() for i in sys.argv[1:]):
            g_lthresh, g_uthresh = (int(i) for i in sys.argv[1:])

    main()


