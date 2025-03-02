# Demostración de creación de imágenes utilizando Yocto Project
# Detección de objetos utilizando Raspberry Pi 5

## Aplicación:
Clonar repositorio

    git clone https://github.com/Tobiasfonseca/DemoYocto.git

Generar ambiente virtual en Ubuntu

    python3 -m venv Demo
    
Activar ambiente

    source Demo/bin/activate

Instalar opencv

    pip install opencv-python

Ingresar a directorio

    cd DemoYocto/App/Deep-Learning-with-OpenCV-DNN-Module/python/detection

Ejecutar archivo

    python3 detect_vid.py

## Configuración de Yocto Project - Poky
### Configuración de Quick Build
Instalación de paquetes

    sudo apt install build-essential chrpath cpio debianutils diffstat file gawk gcc git iputils-ping libacl1 liblz4-tool locales python3 python3-git python3-jinja2 python3-pexpect python3-pip python3-subunit socat texinfo unzip wget xz-utils zstd

Clonar Poky

    git clone git://git.yoctoproject.org/poky

Entrar a la carpeta

    cd poky

Scarthgap release

    git checkout -t origin/scarthgap -b my-scarthgap

Inicializar ambiente

    source oe-init-build-env

Volver al directorio principal

    cd ..
### Recetas
Clonar meta-openembedded

    git clone https://git.openembedded.org/meta-openembedded

Ingresar a meta-openembedded

    cd meta-openembedded

Cambiar branch a Scarthgap

    git checkout -t origin/scarthgap -b my-scarthgap

Volver al directorio principal y repetir para meta-raspberrypi

    $ git clone https://git.yoctoproject.org/meta-raspberrypi
    $ cd meta-raspberrypi
    $ git checkout -t origin/scarthgap -b my-scarthgap

### Añadir nuestra aplicación
Generar directorios para nuestra layer, debemos volver a la carpeta build en la terminal y ejecutar estos comandos:

    $ bitbake-layers create-layer ../meta-mylayer
    $ cd ..
    $ cd meta-mylayer
    $ cd recipes-example
    $ mkdir file-boost
    $ cd file-boost
    $ mkdir files

Generar achivo .bb

    nano file-boost.bb

Pegar lo siguiente:

    SUMMARY = "Recipe to include project files"
    LICENSE = "CLOSED"
    
    SRC_URI = "file://App"
    S = "${WORKDIR}"
    
    do_install() {
        install -d ${D}${bindir}/App
        cp -r App/* ${D}${bindir}/App
    }

Dentro de los directorios generados se encuetra una carpeta llamada file, en esta carpeta es donde vamos a añadir todos los archivos que necesitemos incluir en la imagen. Es decir, la carpeta App del repositorio la vamos a copiar a esta carpeta generada.

### Modificación de archivos .conf
Abrir el archivo bblayers.conf dentro de la carpeta build y copiar lo siguiente:

    # POKY_BBLAYERS_CONF_VERSION is increased each time build/conf/bblayers.conf
    # changes incompatibly
    POKY_BBLAYERS_CONF_VERSION = "2"
    
    BBPATH = "${TOPDIR}"
    BBFILES ?= ""
    
    BBLAYERS ?= " \
      /media/tobi/Yocto/DNN/poky/meta \
      /media/tobi/Yocto/DNN/poky/meta-poky \
      /media/tobi/Yocto/DNN/poky/meta-yocto-bsp \
      /media/tobi/Yocto/DNN/poky/meta-openembedded/meta-oe \
      /media/tobi/Yocto/DNN/poky/meta-openembedded/meta-python \
      /media/tobi/Yocto/DNN/poky/meta-openembedded/meta-multimedia \
      /media/tobi/Yocto/DNN/poky/meta-openembedded/meta-networking \
      /media/tobi/Yocto/DNN/poky/meta-raspberrypi \
      /media/tobi/Yocto/DNN/poky/meta-mylayer \
      "

IMPORTANTE: Modificar la dirección donde tengamos el repositorio clonado de poky, en este caso, /media/tobi/Yocto/DNN 
Abrir el archivo local.conf y pegar lo siguiente

    MACHINE ?= "raspberrypi5"

    IMAGE_INSTALL:append = " openssh \
            python3 \
            python3-pip \
            python3-numpy \
            opencv \
            file-boost"

### Activar DNN
Con la terminal ubicada en poky, ingresar a la siguiente dirección:

    cd meta-openembedded/meta-oe/recipes-support/opencv/

Abrir el archivo .bb

    nano opencv_4.9.0.bb

Buscar la siguiente línea y cambiar de OFF a ON

    PACKAGECONFIG[dnn] = "-DBUILD_opencv_dnn=ON -DPROTOBUF_UPDATE_FILES=ON
    -DBUILD_PROTOBUF=OFF -DCMAKE_CXX_STANDARD=17,
    -DBUILD_opencv_dnn=ON,protobuf protobuf-native,"

### Cocinar!
Volver al directorio build y ejecutar el bitbake

    bitbake core-image-x11

## Instalar RPI Imager
Instale el "quemador" para la tarjeta SD

    sudo apt install rpi-imager

Una vez instalado abra el programa

    rpi-imager

Se abre una ventana como esta:

![image](https://github.com/user-attachments/assets/078c4498-ba2b-4795-b39b-6dd1cee3d785)

Seleccione CHOOSE OS, encuentre la opción "Use custom"

La imagen va a estar disponible en la siguiente ruta poky/build/tmp/deploy/images/raspberrypi5

NOTA: hay que seleccionar que el buscador de archivos permita ver todos los archivos (esquina inferior derecha) y se selecciona la opción core-image-x11-raspberrypi5.rootfs.wic.bz2

Luego se selecciona la memoria SD para flashear y se inicia con Write.

Una vez quemada la imagen, inserte la SD en la Raspberry Pi, conecte la cámara, cable de red y alimentación.

## Conexión SSH
Busque la RPi con este comando dentro de su red

    sudo arp-scan --localnet

Puede que aparezca sin nombre, si eso sucede desconecte la Pi y busca los dispositivos en la red, vuelva a conectar la pi e identifique cual es la dirección IP que aparece.

Realice la conexión

    ssh -X root@192.168.0.100

Mueva la terminal a la dirección de la app y ejecute la app

    $ cd ..
    $ cd ..
    $ cd usr/bin/App/Deep-Learning-with-OpenCV-DNN-Module/python/detection
    $ python3 detect_vid.py

![image](https://github.com/user-attachments/assets/2a949144-dbaa-45fa-a034-1c4ecb2b9c9f)
