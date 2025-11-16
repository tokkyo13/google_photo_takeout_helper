import os
import json
from pathlib import Path
import shutil

# 設定
INPUT_FOLDER = "./Google フォト"
OUTPUT_FOLDER = "./out"

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


def main():
    """メイン処理"""
    if not os.path.exists(INPUT_FOLDER):
        print(f"エラー: フォルダが見つかりません - {INPUT_FOLDER}")
        return

    # 出力フォルダの作成
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"出力フォルダを作成しました: {OUTPUT_FOLDER}\n")

    image_files = []

    # 入力フォルダ配下のすべてのファイルを走査
    for root, dirs, files in os.walk(INPUT_FOLDER):
        for file in files:
            if Path(file).suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(os.path.join(root, file))

    if not image_files:
        print("画像ファイルが見つかりません")
        return

    print(f"処理対象の画像ファイル数: {len(image_files)}\n")

    updated_count = 0
    moved_count = 0

    # 各画像ファイルを処理
    for index, image_path in enumerate(image_files):
        file_name = Path(image_path)
        file_dir = os.path.dirname(image_path)
        json_path = os.path.join(file_dir, f"{file_name}.supplemental-metadata.json")

        # 5000ごとにフォルダ分け
        folder_index = (index // 5000) + 1
        sub_folder = os.path.join(OUTPUT_FOLDER, f"batch_{folder_index}")
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)

        # supplemental-metadata.json ファイルを探す
        print(f"処理中: {file_name}")
        print(f"  - JSON パス: {json_path}")
        if os.path.exists(json_path):
            photo_taken_time = get_photo_taken_time(json_path)
            if photo_taken_time:
                if set_file_time(image_path, photo_taken_time):
                    updated_count += 1
        else:
            print(f"- {Path(image_path).name} (JSON ファイルなし)")

        # ファイルをサブフォルダにコピー
        try:
            output_path = os.path.join(sub_folder, file_name.name)
            shutil.copy2(image_path, output_path)
            print(f"  ✓ {file_name.name} を {sub_folder} にコピーしました")
            moved_count += 1
        except Exception as e:
            print(f"  ✗ {file_name.name} のコピーに失敗しました - {e}")

    print(f"\n処理完了: {updated_count} 個のファイルを更新しました")
    print(f"コピー完了: {moved_count} 個のファイルを {OUTPUT_FOLDER} にコピーしました")


if __name__ == "__main__":
    main()
