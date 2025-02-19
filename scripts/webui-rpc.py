from modules import script_callbacks
from modules import shared
import threading
import time
import os


enable_dynamic_status = True

def start_rpc():
    print('[Discord Rich Presence]  WebUI 디스코드 활동 상태창, 버전 1.0')

    # Check if the required packages are installed, and install them if necessary
    from launch import is_installed, run_pip
    if not is_installed("pypresence"):
        print("[Discord Rich Presence]  누락된 'pypresence' 모듈과 연관된 종속 모듈을 설치하는 중입니다,")
        print("[Discord Rich Presence]  혹시 설치 후 모듈 오류 발생시 -> WebUI 재시작을 해주세요.")
        run_pip("install pypresence", "pypresence")
    else:
        print("[Discord Rich Presence]  'pypresence' 모듈이 이미 설치됨 - 스킵중.")

    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)


    import pypresence

    client_id = "1109920684018257980"

    rpc = pypresence.Presence(client_id)
    rpc.connect()

    time_c = time.time()
    rpc.update(
        state="시작 기다리는중..." if enable_dynamic_status else "유동 활동 상태 - OFF",
        details=model_name,
        large_image="unknown" if enable_dynamic_status else "auto",
        start=int(time_c)
    )

    state_watcher = threading.Thread(target=state_watcher_thread, args=(rpc, time_c), daemon=True)
    state_watcher.start()

    if enable_dynamic_status:
        print("[Discord Rich Presence]  디스코드에서 활동 상태가 활성화되었는지 확인해주세요.")
        print("[Discord Rich Presence]  오류가 없으면 이미 실행 중이어야 합니다.")


def state_watcher_thread(rpc, time_c):
    reset_time = False
    batch_size_r = False
    batch_size = 0
    status = True
    total_progress = 0
    image_to_show = "small_gen_00"
    percent_show = 0

    dict_images = {
        0: "small_gen_00",
        5: "small_gen_05",
        10: "small_gen_10",
        15: "small_gen_15",
        20: "small_gen_20",
        25: "small_gen_25",
        30: "small_gen_30",
        35: "small_gen_35",
        40: "small_gen_40",
        45: "small_gen_45",
        50: "small_gen_50",
        55: "small_gen_55",
        60: "small_gen_60",
        65: "small_gen_65",
        70: "small_gen_70",
        75: "small_gen_75",
        80: "small_gen_80",
        85: "small_gen_85",
        90: "small_gen_90",
        95: "small_gen_95",
        100: "small_gen_100"
    }

    while True:

        checkpoint_info = shared.sd_model.sd_checkpoint_info
        model_name = os.path.basename(checkpoint_info.filename)
        model_name = model_name.split('.')
        model_name = model_name[0]

        if shared.state.job_count == 0:

            if reset_time == False:
                time_c = int(time.time())
                reset_time = True

            if batch_size_r == True:
                batch_size_r = False
                batch_size = 0

            rpc.update(large_image="a1111",
                       details=model_name + " 모델 사용중",
                       state="대기중",
                       start=time_c)
        else:
            if reset_time == True:
                time_c = int(time.time())
                reset_time = False

            if batch_size_r == False:
                batch_size = get_batch_size()
                if batch_size != 0:
                    batch_size_r = True
            if shared.total_tqdm._tqdm is not None:

                if status:
                    total_progress = shared.state.sampling_steps * shared.state.job_count
                    status = False

                progress = shared.total_tqdm._tqdm.n

                percent_progress = progress / total_progress * 100


            else:
                percent_progress = 0

            for image in dict_images:
                if image >= int(percent_progress):
                    image_to_show = dict_images[image]
                    percent_show = image
                    break

            rpc.update(large_image="a1111_gen",
                       small_image=image_to_show,
                       large_text="생성중",
                       small_text=f"{percent_show}%",
                       details=model_name + " 모델 사용중",
                       state=f'생성중 {shared.state.job_count * batch_size} 초당 이미지 수',
                       start=time_c)

        time.sleep(2)


def on_ui_tabs():
    start_rpc()
    return []


def get_batch_size():
    if shared.state.current_latent != None:
        x = shared.state.current_latent.size()
        x = x[0]
        return x
    else:
        return 0


script_callbacks.on_ui_tabs(on_ui_tabs)
