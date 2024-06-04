import os
import subprocess
from tqdm import tqdm

def check_video(file_path):
    # Comando FFmpeg para verificar o arquivo de vídeo
    command = ['ffmpeg', '-v', 'error', '-i', file_path, '-f', 'null', '-']
    
    try:
        # Executa o comando FFmpeg
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        # Retorna False se o vídeo não estiver funcional
        return False

def scan_videos(directory):
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
        if not check_video(file_path):
            # Adiciona ao log se o vídeo não estiver funcional
            error_log.append(file_path)
            print(f"Erro no vídeo: {file_path}")
    
    # Escreve o log de erros em um arquivo
    with open('log.txt', 'w') as log_file:
        for error in error_log:
            log_file.write(f"{error}\n")

if __name__ == "__main__":
    # Obtém o diretório atual
    current_directory = os.getcwd()
    scan_videos(current_directory)