import os
import json
import zipfile
import re
import time

def zip_files_and_folders(file_paths, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.dirname(file_path)))
            else:
                if file_path.startswith('clothes/'):
                    zipf.write(file_path, file_path)
                else:
                    zipf.write(file_path, os.path.basename(file_path))

def list_files_and_subdirectories(directory, output_dict):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), directory)
            if not file_path.endswith('png') and not file_path.endswith('gif'):
                output_dict["additionFile"].append('img/' + file_path.replace("\\", "/"))
            else:
                output_dict["imgFileList"].append('img/' + file_path.replace("\\", "/"))

def generate_files_with_text(folder_path, file_list):
    for filename in file_list:
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('[\n]')

# Check which folders are missing
missing_folders = []
if not os.path.exists('clothes'):
    missing_folders.append('clothes')
if not os.path.exists('img'):
    missing_folders.append('img')
    
# flag to check if the generation happened
files_generated = False

if missing_folders:
    print("Required files missing. Generating the necessary files and folders for the process...")
    if 'clothes' in missing_folders:
        type_list = ['face.json', 'feet.json', 'genitals.json', 'hands.json', 'handheld.json', 'head.json',
                     'legs.json', 'neck.json', 'upper.json', 'lower.json', 'under_upper.json',
                     'under_lower.json', 'over_upper.json', 'over_lower.json', 'over_head.json']
        os.makedirs('clothes', exist_ok=True)
        generate_files_with_text('clothes', type_list)
    if 'img' in missing_folders:
        os.makedirs('img', exist_ok=True)
    files_generated = True

# Only show instructions if files/folders were generated just now
if files_generated:
    # Wait 4 seconds
    time.sleep(4)
    # this is so the previous print gets deleted, just makes it flow better
    os.system('cls' if os.name == 'nt' else 'clear')
    print("The necessary files and folders have been created.\n")
    # Wait 2 seconds    
    time.sleep(2)
    print("Add all the clothing information to the \".json\" files inside the newly generated \"clothes\" folder. Please check INSTRUCTION!.txt for more information")
    print("Add all mod images to the newly generated \"img\" folder following the default DoL structure for clothes.")
    print("e.g. img/clothes/upper/cute dress/full.png.\n")
    # Wait 3 seconds    
    time.sleep(3)
    input("Press ENTER to proceed once you have completed the steps above.\nIf you want to stop for now and continue later, simply close this window.\n")

if not files_generated:
    print("Remember! Add all the clothing information to the \".json\" files inside your \"clothes\" folder. Please check INSTRUCTION!.txt for more information")
    print("Add all mod images to your \"img\" folder following the default DoL structure for clothes.")
    print("e.g. img/clothes/upper/cute dress/full.png.\n")
    # Wait 1 seconds    
    time.sleep(1)
    input("Press ENTER to proceed once you have completed the steps above.\nIf you want to stop for now and continue later, simply close this window.\n")



dir_path = 'clothes' 
for fn in os.listdir(dir_path):
    if not fn.endswith('.json'): continue
    p = os.path.join(dir_path, fn)
    with open(p, 'r', encoding='utf8') as f: c = f.read()
    c = c.replace('""','"')
    c = re.sub(r'"(\s*{)', r'\1', c)
    c = re.sub(r'}(\s*)"', r'}\1', c)
    c = re.sub(r',\s*([\]\}])', r'\1', c)
    c = re.sub(r'"\s*(?=\{)', '', c)
    c = c.strip()
    if not c.startswith('['): c = '[\n' + c
    idx = c.rfind('}')
    c = (c[:idx+1].rstrip() if idx != -1 else re.sub(r'\]\s*$', '', c)) + '\n]'
    c = re.sub(
        r'(?m)^(?P<indent>[ \t]*)(?P<author_line>"author"\s*:\s*".*?")\s*,\s*}',
        r'\g<indent>\g<author_line>\n\g<indent>},',
        c
    )
    # gotta solve the blank places issue
    c = c.replace(': ",', ': "", ')
    
    lines = c.splitlines()
    # find all the damn }, and }
    brace_lines = [i for i, line in enumerate(lines) if line.strip().endswith('}') or line.strip().endswith('},')]

    for i, line_num in enumerate(brace_lines):
        line = lines[line_num].rstrip()
        
        # Check if its the last }
        is_last = (i == len(brace_lines) - 1)

        if is_last:
            # If its the LAST } then make sure it ends with just } and no commas
            if line.endswith('},'):
                lines[line_num] = line[:-1]
        else:
            # If its NOT the last, then make sure it ends with },
            if line.endswith('}') and not line.endswith('},'):
                lines[line_num] = line + ','

    c = '\n'.join(lines)    
    c = re.sub(r'}\s*,\s*{', '},\n\t{', c)
    
    # i just think it looks better like this idk
    c = c.replace('},\n\t{', '},\n{')
    
    # bandaid fixing some stuff
    c = c.replace(': ["],', ': [""],')
    c = c.replace(': "}\n]', ': ""\n}\n]')
    c = c.replace(': "},', ': ""\n},')
    c = c.replace(': "\n', ': ""\n')
    c = c.replace(': "\t\n', ': ""\n')
    c = c.replace(': "\t\t\n', ': ""\n')
    c = c.replace(': "\t\t\t\n', ': ""\n')
    c = c.replace(': "\t\t\t\t\n', ': ""\n')
    c = c.replace('[\n\n]', '[\n]')
    c = c.replace('[\n\n\n]', '[\n]')
    c = c.replace('[\n\n\n\n]', '[\n]')
    c = c.replace('[\n\n\n\n\n]', '[\n]')
    c = c.replace('[\n\n\n\n\n\n]', '[\n]')
    c = c.replace('[\n\n\n\n\n\n\n]', '[\n]')
    with open(p, 'w', encoding='utf8') as f: f.write(c)

output_dict = {}
output_dict['name'] = input('请输入模组名称 / Input Mod Name:')
output_dict['version'] = input('请输入类似于1.0.0的模组版本号 / Please enter a module version number similar to 1.0.0:')
print(f'模组生成中请稍等... / Please wait for a while in the module generation...')
output_dict['styleFileList'] = []
output_dict['scriptFileList'] = []
output_dict['tweeFileList'] = []
output_dict['additionFile'] = []
output_dict['imgFileList'] = []
list_files_and_subdirectories('img', output_dict)
output_dict['addonPlugin'] = [
    {
      "modName": "ModdedClothesAddon",
      "addonName": "ModdedClothesAddon",
      "modVersion": "^1.1.0",
      "params": {
        "clothes": [
          {
            "key": "face",
            "filePath": "clothes/face.json"
          },
          {
            "key": "feet",
            "filePath": "clothes/feet.json"
          },
          {
            "key": "genitals",
            "filePath": "clothes/genitals.json"
          },
          {
            "key": "hands",
            "filePath": "clothes/hands.json"
          },
          {
            "key": "handheld",
            "filePath": "clothes/handheld.json"
          },
          {
            "key": "head",
            "filePath": "clothes/head.json"
          },
          {
            "key": "legs",
            "filePath": "clothes/legs.json"
          },
          {
            "key": "neck",
            "filePath": "clothes/neck.json"
          },
          {
            "key": "upper",
            "filePath": "clothes/upper.json"
          },
          {
            "key": "lower",
            "filePath": "clothes/lower.json"
          },
          {
            "key": "under_upper",
            "filePath": "clothes/under_upper.json"
          },
          {
            "key": "under_lower",
            "filePath": "clothes/under_lower.json"
          },
          {
            "key": "over_upper",
            "filePath": "clothes/over_upper.json"
          },
          {
            "key": "over_lower",
            "filePath": "clothes/over_lower.json"
          },
          {
            "key": "over_head",
            "filePath": "clothes/over_head.json"
          }
        ]
      }
    },
    {
      "modName": "ModLoader DoL ImageLoaderHook",
      "addonName": "ImageLoaderAddon",
      "modVersion": "^2.3.0",
      "params": [
      ]
    }
  ]
output_dict['dependenceInfo'] = [
    {
      "modName": "ModdedClothesAddon",
      "version": "^1.1.0"
    },
    {
      "modName": "ModLoader DoL ImageLoaderHook",
      "version": "^2.3.0"
    }
  ]

# check each clothes json and only add the ones that are not empty
clothes_types = ['face', 'feet', 'genitals', 'hands', 'handheld', 'head',
                 'legs', 'neck', 'upper', 'lower', 'under_upper',
                 'under_lower', 'over_upper', 'over_lower', 'over_head']

real_clothes = []  # the clothes that wiill go in the boot.json
real_clothes_files = []  # The clothes files that should go in the zip

# Loop through all the clothes types we want to check
for c in clothes_types:
    # Make sure the file is like, clothes/upper.json, clothes/lower.json, etc.
    file_name = 'clothes/' + c + '.json'
    if os.path.exists(file_name):
        # Open the file and read the contentssss
        f = open(file_name, 'r', encoding='utf-8')
        stuff = f.read()
        f.close()
        stuff2 = stuff.strip()
        # If the file is empty (just [] or [\n] variation or nothing) skipppppp
        if stuff2 == '[]' or stuff2 == '[\n]' or stuff2 == '[\n\n]' or stuff2 == '[\n\n\n]' or stuff2 == '[\n\n\n\n]' or stuff2 == '':
            print('Skipping empty clothes .json file:', file_name)
        else:
            # hehe you're not REAL CLOTHES UNLESS YOU AREN'T EMPTY 😈 GET OUT POSERS🥶⛓️
            print('Including clothes .json file with content:', file_name)
            real_clothes.append({
                "key": c,
                "filePath": file_name
            })
            real_clothes_files.append(file_name)
    else:
        print('Skipping missing clothes file:', file_name)

# Replace the default clothes .json list in the boot.json with only the ""real"" ones
output_dict['addonPlugin'][0]['params']['clothes'] = real_clothes

# 将内容输出到文本文件
with open('boot.json', 'w', encoding='utf-8') as file:
    json.dump(output_dict, file, indent=2, ensure_ascii=False)

# 要压缩的文件和文件夹路径列表 | new commentary: took out the clothes folder from here since we not zipping the entire folder anymore, only the necessary parts
file_paths = ['img', 'boot.json']

# If no clothes files have content, abort zip generation
if not real_clothes_files:
    print(f"\nNo content found in any of the clothes/.json files, {output_dict['name']}.zip generation aborted.")
    print("Try again after you've filled the required information.")
    if os.path.exists('boot.json'):
        os.remove('boot.json')
else:
    # Add the real clothes json files inside a clothes/ folder in the zip, not the same path as boot file or img folder
    for cfile in real_clothes_files:
        file_paths.append(cfile)

    # 压缩后的文件名
    zip_name = output_dict['name'] + '.zip'
    zip_files_and_folders(file_paths, zip_name)
    os.remove('boot.json')
    print()
    print(f'模组生成完成 / Mod Generation is finished: {zip_name}')
# Keep window open until user presses a key, just cuz I like seeing the Mod Generation is finished message, very dopamine. Also lets ppl be able to check which .json files were skipped and which weren't
input("\nPress ENTER to exit...")
