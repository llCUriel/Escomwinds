#!/bin/bash

echo '1-Configurar tap0'
echo '2-Quitar tap0'
read opt

case $opt in
    1)
        sudo tunctl -t tap0
        sudo ip addr add 10.200.200.21/30 dev tap0
        sudo ip link set dev tap0 up
        ip route
        echo ''
        echo 'Inserta la ip que aparece en el comando despues de default via'
        read ip
        echo 'Inserta la interfaz que aparace justo despues de dev'
        read inter

        sudo ip route del default via $ip dev $inter
        sudo ip route add default via 10.200.200.22 dev tap0

        echo 'Tap0 Configurada'
        echo $ip > tap0conf.bk
        echo $inter >> tap0conf.bk
        ;;
    2)
        { read -r ip; read -r inter; } < tap0conf.bk
        sudo ip route del default via 10.200.200.22 dev tap0
        sudo ip route add default via $ip dev $inter
        ;;
    *)
        echo ':v'
        ;;
esac
