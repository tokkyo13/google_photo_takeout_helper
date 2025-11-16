import os
import json
from pathlib import Path
import shutil

# 設定
DL_DIR = "./download"
EXTRACT_DIR = "./extract"
MERGED_DIR = "./merge"

IMAGE_EXTENSIONS = {
    ".avi",
    ".bmp",
    ".gif",
    ".heic",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".png",
    ".webp",
}


def get_photo_taken_time(json_path):
    """JSON ファイルから photoTakenTime を取得"""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "photoTakenTime" in data:
                return data["photoTakenTime"]["timestamp"]
    except Exception as e:
        print(f"エラー: {json_path} の読み込みに失敗しました - {e}")
    return None


def set_file_time(file_path, timestamp_str):
    """ファイルの作成日時を設定"""
    try:
        timestamp_sec = int(timestamp_str)
        os.utime(file_path, (timestamp_sec, timestamp_sec))
        print(f"✓ {Path(file_path).name} の作成日時を更新しました")
        return True
    except Exception as e:
        print(f"✗ {Path(file_path).name} の作成日時更新に失敗しました - {e}")
        return False
    
def unpack_zip(dl_path, extract_path):
    """フォルダ内のZIP ファイルをすべて解凍"""
    for root, dirs, files in os.walk(dl_path):
        for file in files:
            if Path(file).suffix.lower() == ".zip":
                zip_path = os.path.join(root, file)
                try:
                    shutil.unpack_archive(zip_path, extract_path)
                    print(f"✓ {file} を解凍しました")
                except Exception as e:
                    print(f"✗ {file} の解凍に失敗しました - {e}")


def get_year_from_timestamp(timestamp_str):
    """タイムスタンプから年を取得"""
    try:
        timestamp_sec = int(timestamp_str)
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp_sec)
        return dt.year
    except Exception as e:
        print(f"エラー: タイムスタンプの変換に失敗しました - {e}")
    return None


def main():
    """メイン処理"""
    # # ZIP ファイル保存フォルダの存在確認
    # if not os.path.exists(DL_DIR):
    #     print(f"エラー: ダウンロードフォルダが存在しません - {DL_DIR}")
    #     return

    # # 出力フォルダの作成
    # if not os.path.exists(EXTRACT_DIR):
    #     os.makedirs(EXTRACT_DIR)
    
    # if not os.path.exists(MERGED_DIR):
    #     os.makedirs(MERGED_DIR)

    # # ZIP ファイルの解凍
    # unpack_zip(DL_DIR, EXTRACT_DIR)

    # 入力フォルダ配下のすべてのファイルを走査
    image_files = []
    for root, dirs, files in os.walk(EXTRACT_DIR):
        for file in files:
            if Path(file).suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(os.path.join(root, file))

    if not image_files:
        print("画像ファイルが見つかりません")
        return

    print(f"処理対象の画像ファイル数: {len(image_files)}\n")

    # 各画像ファイルを処理
    updated_count = 0
    moved_count = 0

    for index, image_path in enumerate(image_files):
        file_name = Path(image_path)
        file_dir = os.path.dirname(image_path)
        
        # ファイル名を含むJSONファイルを検索
        json_path = None
        for file in os.listdir(file_dir):
            if file.startswith(file_name.name) and file.endswith(".json"):
                json_path = os.path.join(file_dir, file)
                break

        # JSONファイルから年を取得してフォルダ分け
        year_folder = "unknown"
        print(f"処理中: {file_name}")
        print(f"  - JSON パス: {json_path}")
        if json_path and os.path.exists(json_path):
            photo_taken_time = get_photo_taken_time(json_path)
            if photo_taken_time:
                if set_file_time(image_path, photo_taken_time):
                    updated_count += 1
                year = get_year_from_timestamp(photo_taken_time)
                if year:
                    year_folder = str(year)
        else:
            print(f"- {Path(image_path).name} (JSON ファイルなし)")

        # 年ごとのフォルダを作成
        sub_folder = os.path.join(MERGED_DIR, year_folder)
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)

        # ファイルをサブフォルダにコピー
        try:
            output_path = os.path.join(sub_folder, file_name.name)
            
            # 同名ファイルが存在する場合、サフィックスを付ける
            if os.path.exists(output_path):
                stem = file_name.stem
                suffix = file_name.suffix
                counter = 1
                while os.path.exists(output_path):
                    new_name = f"{stem}_{counter}{suffix}"
                    output_path = os.path.join(sub_folder, new_name)
                    counter += 1
            
            shutil.copy2(image_path, output_path)
            print(f"  ✓ {Path(output_path).name} を {sub_folder} にコピーしました")
            moved_count += 1
        except Exception as e:
            print(f"  ✗ {file_name.name} のコピーに失敗しました - {e}")

    print(f"\n処理完了: {updated_count} 個のファイルを更新しました")
    print(f"コピー完了: {moved_count} 個のファイルを {MERGED_DIR} にコピーしました")


if __name__ == "__main__":
    main()
