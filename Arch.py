import os
import subprocess

def run_command(command):
    """Ejecuta un comando del sistema y maneja errores"""
    try:
        print(f"Ejecutando: {command}")
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando {e.cmd}: {e.returncode}")
        raise

def configure_pacman():
    """Configura Pacman"""
    run_command("pacman -Sy --noconfirm")

def install_base_packages():
    """Instala los paquetes base de Arch Linux y el entorno de escritorio BSPWM"""
    run_command("pacstrap /mnt base linux linux-firmware xorg-server xorg-apps xorg-xinit bspwm sxhkd dmenu rofi termite feh")

def generate_fstab():
    """Genera el archivo fstab"""
    run_command("genfstab -U /mnt >> /mnt/etc/fstab")

def chroot_and_configure():
    """Chroot a la nueva instalación y configura el sistema"""
    run_command("arch-chroot /mnt")

    # Configura el timezone
    run_command("ln -sf /usr/share/zoneinfo/Region/City /etc/localtime")
    run_command("hwclock --systohc")

    # Configura la localización
    run_command("echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen")
    run_command("locale-gen")
    run_command("echo 'LANG=en_US.UTF-8' > /etc/locale.conf")

    # Configura la red
    run_command("echo 'archlinux' > /etc/hostname")
    run_command("echo '127.0.0.1 localhost' >> /etc/hosts")
    run_command("echo '::1 localhost' >> /etc/hosts")
    run_command("echo '127.0.1.1 archlinux.localdomain archlinux' >> /etc/hosts")

    # Configura mkinitcpio
    run_command("mkinitcpio -P")

    # Configura GRUB
    run_command("pacman -Sy grub --noconfirm")
    run_command("grub-install --target=i386-pc /dev/sda")
    run_command("grub-mkconfig -o /boot/grub/grub.cfg")

    # Configura la contraseña de root
    run_command("echo 'root:password' | chpasswd")

    # Configura BSPWM
    run_command("mkdir -p /root/.config/bspwm /root/.config/sxhkd")
    run_command("curl -o /root/.config/bspwm/bspwmrc https://raw.githubusercontent.com/bspwm/bspwm/master/examples/bspwmrc")
    run_command("chmod +x /root/.config/bspwm/bspwmrc")
    run_command("curl -o /root/.config/sxhkd/sxhkdrc https://raw.githubusercontent.com/bspwm/bspwm/master/examples/sxhkdrc")

    # Configura .xinitrc para iniciar BSPWM
    run_command("echo 'exec bspwm' > /root/.xinitrc")

    # Configura el archivo de perfil de usuario
    run_command("useradd -m -G wheel -s /bin/bash user")
    run_command("echo 'user:password' | chpasswd")
    run_command("echo '%wheel ALL=(ALL) ALL' >> /etc/sudoers")

def main():
    # Actualiza el sistema y configura Pacman
    configure_pacman()
    
    # Formatea la partición e instala los paquetes base
    run_command("mkfs.ext4 /dev/sda1")
    run_command("mount /dev/sda1 /mnt")
    install_base_packages()
    
    # Genera fstab y configura el sistema
    generate_fstab()
    chroot_and_configure()
    
    print("La instalación de Arch Linux y BSPWM ha finalizado. ¡Reinicia para completar la instalación!")

if __name__ == "__main__":
    main()

