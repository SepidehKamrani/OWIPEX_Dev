#!/usr/bin/env python3

import time
import subprocess

def main():
    print("Das Timer-Programm wurde gestartet.")
    
    # Wartezeit in Sekunden (hier 10 Sekunden als Beispiel)
    wait_time = 10
    
    print(f"Das Hauptprogramm wird in {wait_time} Sekunden gestartet.")
    time.sleep(wait_time)
    
    print("Starte das Hauptprogramm mit sudo...")
    subprocess.run(["sudo", "python3", "/home/owipex/v1.0/h2o.py"])

if __name__ == "__main__":
    main()