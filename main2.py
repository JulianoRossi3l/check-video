import os
import subprocess
from tqdm import tqdm

def detect_gpu():
    # Verifica a presença de GPU NVIDIA
    try:
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return 'cuda'
    except FileNotFoundError:
        pass
    
    # Verifica a presença de GPU Intel
    try:
        result = subprocess.run(['vainfo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if 'Intel' in result.stdout.decode('utf-8'):
            return 'qsv'
    except FileNotFoundError:
        pass

    # Verifica a presença de GPU AMD
    try:
        result = subprocess.run(['vainfo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if 'AMD' in result.stdout.decode('utf-8'):
            return 'vaapi'
    except FileNotFoundError:
        pass

    # Retorna None se nenhuma GPU for detectada
    return None

def check_video(file_path, hwaccel, max_threads):
    # Comando FFmpeg para verificar o arquivo de vídeo
    command = ['ffmpeg', '-v', 'error', '-i', file_path, '-f', 'null', '-']
    
    if hwaccel != 'none':
        # Adiciona a opção de aceleração de hardware se especificada
        command.insert(3, '-hwaccel')
        command.insert(4, hwaccel)
    
    if max_threads is not None:
        command.insert(-1, '-threads')
        command.insert(-1, str(max_threads))

    try:
        # Executa o comando FFmpeg
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        # Retorna False se o vídeo não estiver funcional
        return False

def scan_videos(directory, hwaccel, max_threads):
    error_log = []
    # Lista para armazenar todos os arquivos de vídeo
    video_files = []

    # Percorre todas as pastas e subpastas
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mp4'):
                video_files.append(os.path.join(root, file))

    # Inicializa a barra de progresso
    for file_path in tqdm(video_files, desc="Verificando vídeos"):
        if not check_video(file_path, hwaccel, max_threads):
            # Adiciona ao log se o vídeo não estiver funcional
            error_log.append(file_path)
            print(f"Erro no vídeo: {file_path}")
    
    # Escreve o log de erros em um arquivo
    with open('log.txt', 'w') as log_file:
        for error in error_log:
            log_file.write(f"{error}\n")

if __name__ == "__main__":
    import argparse

    # Argument parser para configurar as opções de linha de comando
    parser = argparse.ArgumentParser(description="Verificar vídeos MP4")
    parser.add_argument("--max-threads", type=int, default=None, help="Número máximo de threads a usar")
    
    args = parser.parse_args()

    # Detecta o tipo de GPU disponível
    hwaccel = detect_gpu()
    
    if hwaccel is None:
        print("Nenhuma GPU compatível encontrada. Usando CPU.")
        hwaccel = 'none'
    
    # Obtém o diretório atual
    current_directory = os.getcwd()
    scan_videos(current_directory, hwaccel, args.max_threads)
