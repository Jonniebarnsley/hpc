#!/bin/bash

# function to count the number of files in a directory which match a given pattern.
count_files() {
    local directory="$1"
    local pattern="$2"
    find "$directory" -maxdepth 1 -type f -name "$pattern" | wc -l
}

# add leading zeros to numbers
digits() {
   echo "test" 
}

# matches mask values with IMBIE basins
getIMBIEbasin() {
    local ID="$1"
    case $ID in
    0)  echo "WAIS" ;;
    1)  echo "EAIS" ;;
    2)  echo "APIS" ;;
    esac
}

# matches mask values with Rignot basins
getRignotbasin() {
    local ID="$1"
    case $ID in
    0)      echo "Islands"  ;;
    1)      echo "H-Hp"     ;;
    2)      echo "F-G"      ;;
    3)      echo "E-Ep"     ;;
    4)      echo "D-Dp"     ;;
    5)      echo "Cp-D"     ;;
    6)      echo "B-C"      ;;
    7)      echo "A-Ap"     ;;
    8)      echo "Jpp-K"    ;;
    9)      echo "G-H"      ;;
    10)     echo "Dp-E"     ;;
    11)     echo "Ap-B"     ;;
    12)     echo "C-Cp"     ;;
    13)     echo "K-A"      ;;
    14)     echo "J-Jpp"    ;;
    15)     echo "Ipp-J"    ;;
    16)     echo "I-Ipp"    ;;
    17)     echo "Hp-I"     ;;
    18)     echo "Ep-F"     ;;
    esac
}

# checks mask filename and uses appropriate basin-finding function
getBasin() {
    local MASK="$1"
    local ID="$2"
    case $MASK in
    *IMBIE*)    getIMBIEbasin $ID           ;;
    *rignot*)   getRignotbasin $ID          ;;
    *zwally*)   echo $(printf "%02d" $ID)   ;;
    "")         echo "AIS"                  ;;
    esac
}
