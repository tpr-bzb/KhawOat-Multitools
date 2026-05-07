import os
import re
import secrets
import string
import csv
import pandas as pd
import qrcode
import io
import base64
from collections import Counter
from datetime import datetime, timezone


def get_extension(val: str) -> str:
    if val == "EXCEL":
        return ".xlsx"
    if val == "NO EXT":
        return ""
    return f".{val.lower()}"


def list_files_to_process(src_dir: str, src_type: str, src_ext: str) -> list[str]:
    files_to_process = []
    if not os.path.exists(src_dir):
        return []
    for file_name in os.listdir(src_dir):
        full_path = os.path.join(src_dir, file_name)
        if not os.path.isfile(full_path):
            continue
        lower_name = file_name.lower()
        if src_type == "EXCEL" and (lower_name.endswith(".xlsx") or lower_name.endswith(".xls")):
            files_to_process.append(file_name)
        elif src_type == "NO EXT" and "." not in file_name:
            files_to_process.append(file_name)
        elif src_type not in ("EXCEL", "NO EXT") and lower_name.endswith(src_ext):
            files_to_process.append(file_name)
    return files_to_process


def build_password(length: int, include_upper: bool, include_lower: bool, include_numbers: bool, include_symbols: bool) -> str:
    chars = ""
    if include_upper:
        chars += string.ascii_uppercase
    if include_lower:
        chars += string.ascii_lowercase
    if include_numbers:
        chars += string.digits
    if include_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not chars:
        return ""
    return "".join(secrets.choice(chars) for _ in range(length))


def epoch_to_local_datetime_text(value: int) -> str:
    epoch = value / 1000 if value > 9999999999 else value
    return datetime.fromtimestamp(epoch, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def ticks_to_local_datetime_text(ticks: int) -> str:
    seconds = (ticks - 621355968000000000) / 10000000
    return datetime.fromtimestamp(seconds, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def analyze_hidden_chars(text: str, anomalies: dict[str, str]) -> list[str]:
    found = []
    char_counter = Counter(text)
    for char, name in anomalies.items():
        count = char_counter.get(char, 0)
        if count > 0:
            found.append(f"⚠️ พบ {name} จำนวน {count} จุด")

    ctrl_count = sum(
        count for ch, count in char_counter.items()
        if ord(ch) < 32 and ord(ch) not in (9, 10, 13)
    )
    if ctrl_count > 0:
        found.append(f"⚠️ พบ Control Character (อักขระควบคุม) จำนวน {ctrl_count} จุด")
    return found


def clean_hidden_text(text: str, anomalies: dict[str, str]) -> str:
    output = text
    for char in anomalies.keys():
        output = output.replace(char, "")
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", output)

def process_hidden_char_file(path: str, anomalies: dict[str, str]):
    """Analyzes and prepares cleaned data for a file."""
    if not os.path.exists(path):
        return None, "❌ ไม่พบไฟล์"
    
    rep = []
    cleaned_data = None
    try:
        if path.lower().endswith(('.xlsx', '.xls', '.csv')):
            df = pd.read_excel(path) if not path.lower().endswith('.csv') else pd.read_csv(path)
            cnt = 0
            for r_idx, row in df.iterrows():
                for col, val in row.items():
                    if isinstance(val, str):
                        for char, desc in anomalies.items():
                            if char in val:
                                rep.append(f"📍 แถว {r_idx+1}, '{col}': {desc}")
                                cnt += 1
            if cnt > 0:
                for c in anomalies:
                    df = df.replace(c, '', regex=True)
                cleaned_data = df
                status_msg = f"🔎 พบ {cnt} จุด:\n" + "\n".join(rep)
            else:
                status_msg = "✅ ไฟล์สะอาด!"
        else:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            new_l = []
            for i, l in enumerate(lines):
                found_in_line = False
                for c, d in anomalies.items():
                    if c in l:
                        rep.append(f"📍 บรรทัด {i+1}: {d}")
                        found_in_line = True
                for c in anomalies:
                    l = l.replace(c, '')
                new_l.append(l)
            if rep:
                cleaned_data = "".join(new_l)
                status_msg = f"🔎 พบ {len(rep)} จุด:\n" + "\n".join(rep)
            else:
                status_msg = "✅ ไฟล์สะอาด!"
        return cleaned_data, status_msg
    except Exception as ex:
        return None, f"❌ Error: {ex}"

def generate_qr_base64(text: str) -> str:
    if not text:
        return ""
    qr = qrcode.QRCode()
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buff = io.BytesIO()
    try:
        img.save(buff, format="PNG")
    except:
        img.save(buff)
    return base64.b64encode(buff.getvalue()).decode()

def process_file_split_streaming(
    src_dir: str, 
    files_to_process: list[str], 
    out_dir: str, 
    base_name: str, 
    size: int, 
    has_header: bool, 
    src_ext_label: str, 
    out_ext_label: str,
    out_ext_dot: str,
    status_callback=None, # Function to call for updates
    cancel_check=None    # Function to check if cancellation requested
):
    total_rows_processed = 0
    file_counter = 1
    current_chunk_data = []
    header_row = None
    error_files = []

    def save_chunk(rows, count):
        out_path = os.path.join(out_dir, f"{base_name}_{count}{out_ext_dot}")
        if out_ext_label == "EXCEL":
            df_out = pd.DataFrame(rows, columns=header_row)
            df_out.to_excel(out_path, index=False, header=has_header, engine='openpyxl')
        else:
            with open(out_path, 'w', encoding='utf-8-sig', newline='') as f_out:
                writer = csv.writer(f_out)
                if has_header and header_row:
                    writer.writerow(header_row)
                writer.writerows(rows)

    for filename in files_to_process:
        if cancel_check and cancel_check(): break
        full_path = os.path.join(src_dir, filename)
        if status_callback: status_callback(f"Processing: {filename}", force=True)
        
        try:
            file_rows = []
            if filename.lower().endswith(('.xlsx', '.xls')):
                df_in = pd.read_excel(full_path, header=0 if has_header else None, dtype=str)
                df_in = df_in.fillna("")
                if has_header and header_row is None:
                    header_row = df_in.columns.tolist()
                file_rows = df_in.values.tolist()
            else:
                with open(full_path, 'r', encoding='utf-8-sig', errors='ignore', newline='') as f_in:
                    reader = csv.reader(f_in)
                    first_row = True
                    for row in reader:
                        if has_header and first_row:
                            if header_row is None:
                                header_row = row
                            first_row = False
                            continue
                        file_rows.append(row)

            for r in file_rows:
                if cancel_check and cancel_check(): break
                current_chunk_data.append(r)
                total_rows_processed += 1
                
                if len(current_chunk_data) >= size:
                    save_chunk(current_chunk_data, file_counter)
                    if status_callback: status_callback(f"Created file {file_counter}...", force=True)
                    file_counter += 1
                    current_chunk_data = []
                elif total_rows_processed % 1000 == 0:
                    if status_callback: status_callback(f"Rows: {total_rows_processed:,}")
                    
        except Exception as ex:
            error_files.append(f"{filename} ({ex})")

    if current_chunk_data and not (cancel_check and cancel_check()):
        save_chunk(current_chunk_data, file_counter)
        file_counter += 1

    return {
        "total_rows": total_rows_processed,
        "files_created": file_counter - 1,
        "errors": error_files
    }

def find_binary_indices(binary_str: str) -> list[int]:
    """Finds left-to-right 1-based indices of '1's in a string."""
    return [i + 1 for i, char in enumerate(binary_str) if char == '1']


def search_json(data, keyword, path=""):
    """Recursively search for keyword in keys or values of a JSON object."""
    results = []
    keyword_lower = str(keyword).lower()

    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{path}.{k}" if path else k
            if keyword_lower in str(k).lower() or keyword_lower in str(v).lower():
                results.append(current_path)
            if isinstance(v, (dict, list)):
                results.extend(search_json(v, keyword, current_path))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            current_path = f"{path}[{i}]"
            if keyword_lower in str(v).lower():
                results.append(current_path)
            if isinstance(v, (dict, list)):
                results.extend(search_json(v, keyword, current_path))
    return results


def is_base64_json(text: str) -> bool:
    """Checks if a string is a base64 encoded JSON."""
    try:
        if not text or len(text) < 4: return False
        decoded = base64.b64decode(text, validate=True).decode('utf-8')
        json.loads(decoded)
        return True
    except:
        return False


def json_to_csv_text(data) -> str:
    """Converts JSON (list of dicts) to CSV string."""
    if not isinstance(data, list) or not data:
        # If it's a single dict, wrap it
        if isinstance(data, dict):
            data = [data]
        else:
            return ""
    
    output = io.StringIO()
    # Flatten if nested? For now, just top level
    df = pd.DataFrame(data)
    df.to_csv(output, index=False, encoding='utf-8-sig')
    return output.getvalue()


def csv_to_json_data(csv_text: str):
    """Converts CSV string to JSON list of dicts."""
    if not csv_text.strip():
        return []
    
    input_io = io.StringIO(csv_text.strip())
    df = pd.read_csv(input_io)
    # Fill NaN to avoid invalid JSON
    df = df.fillna("")
    return df.to_dict(orient='records')


def compare_json(obj1, obj2, path="root"):
    """Deeply compare two JSON objects and return differences."""
    diffs = []
    
    if type(obj1) != type(obj2):
        diffs.append(f"Type mismatch at {path}: {type(obj1).__name__} vs {type(obj2).__name__}")
        return diffs

    if isinstance(obj1, dict):
        keys1 = set(obj1.keys())
        keys2 = set(obj2.keys())
        
        # Keys in 1 but not in 2
        for k in keys1 - keys2:
            diffs.append(f"❌ Removed key: {path}.{k}")
        
        # Keys in 2 but not in 1
        for k in keys2 - keys1:
            diffs.append(f"➕ Added key: {path}.{k}")
            
        # Common keys
        for k in keys1 & keys2:
            diffs.extend(compare_json(obj1[k], obj2[k], f"{path}.{k}"))
            
    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            diffs.append(f"⚠️ List length mismatch at {path}: {len(obj1)} vs {len(obj2)}")
        
        for i in range(min(len(obj1), len(obj2))):
            diffs.extend(compare_json(obj1[i], obj2[i], f"{path}[{i}]"))
    else:
        if obj1 != obj2:
            diffs.append(f"📝 Value mismatch at {path}: '{obj1}' ➔ '{obj2}'")
            
    return diffs


import hashlib
import requests
import difflib

def get_text_diff(text1: str, text2: str):
    """Compares two strings and returns a list of diff objects."""
    d = difflib.Differ()
    diff = list(d.compare(text1.splitlines(), text2.splitlines()))
    return diff

def calculate_local_hash(filepath):
    """Calculate SHA256 of a local file."""
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

async def check_for_patches(manifest_url: str, base_path: str):
    """
    Checks which files need to be updated.
    Returns a list of files to download.
    """
    try:
        res = requests.get(manifest_url, timeout=10)
        remote_manifest = res.json()
        patches_needed = []
        
        for rel_path, info in remote_manifest.get("files", {}).items():
            local_path = os.path.join(base_path, rel_path)
            local_hash = calculate_local_hash(local_path)
            
            if local_hash != info["hash"]:
                patches_needed.append({
                    "rel_path": rel_path,
                    "url": f"{os.path.dirname(manifest_url)}/{rel_path}",
                    "size": info["size"]
                })
        return patches_needed, remote_manifest["version"]
    except Exception as e:
        print(f"Patch check error: {e}")
        return [], None

async def apply_patch(url: str, dest_path: str):
    """Downloads a single file and saves it to dest_path."""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        res = requests.get(url, timeout=30, stream=True)
        if res.status_code == 200:
            # We use a temporary file to avoid corruption
            temp_path = dest_path + ".tmp"
            with open(temp_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Replace old file
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(temp_path, dest_path)
            return True
    except Exception as e:
        print(f"Apply patch error: {e}")
    return False
