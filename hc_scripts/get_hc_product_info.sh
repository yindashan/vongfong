#!/bin/bash                                                                     
MANUFACTURER=`dmidecode -s system-manufacturer | tr "," " "`
PRODUCT_NAME=`dmidecode -s system-product-name | tr "," " "`
SERIAL_NUMBER=`dmidecode -s system-serial-number | tr "," " "`


echo "MANUFACTURER=$MANUFACTURER,PRODUCT_NAME=$PRODUCT_NAME,SERIAL_NUMBER=$SERIAL_NUMBER | 制造商:$MANUFACTURER,型号:$PRODUCT_NAME,序列号:$SERIAL_NUMBER"

