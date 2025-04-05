#sudo apt-get install python3-pcap
#pip install dpkt

#!/usr/bin/env python3
import sys
import signal
import pcap
import dpkt

class SilentBridge:
    def __init__(self, iface1, iface2):
        self.iface1 = iface1
        self.iface2 = iface2
        self.running = True
        
        # Настройка обработчика сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        
    def stop(self, signum, frame):
        print("\nStopping SilentBridge...")
        self.running = False
        
    def packet_handler(self, timestamp, packet, *args):
        """Обработчик пакетов - просто пересылает их на другой интерфейс"""
        out_adapter = args[0]
        try:
            out_adapter.sendpacket(packet)
        except Exception as e:
            print(f"Error sending packet: {e}")
    
    def run(self):
        """Основной цикл работы моста"""
        print(f"Starting SilentBridge: {self.iface1} <-> {self.iface2}")
        print("Press Ctrl+C to stop...")
        
        # Открываем интерфейсы в режиме promiscuous
        in_adapter = pcap.pcap(name=self.iface1, promisc=True, immediate=True)
        out_adapter = pcap.pcap(name=self.iface2, promisc=True, immediate=True)
        
        # Настраиваем захват всех Ethernet-кадров
        in_adapter.setfilter('')
        
        try:
            # Основной цикл обработки пакетов
            while self.running:
                # Обрабатываем пакеты с таймаутом для проверки running
                in_adapter.dispatch(1, self.packet_handler, out_adapter)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("SilentBridge stopped.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <interface1> <interface2>")
        print("Example: sudo ./silentbridge.py eth0 eth1")
        sys.exit(1)
    
    # Требуем права root для работы с raw сокетами
    if not (hasattr(os, 'geteuid') and os.geteuid() == 0):
        print("Error: This program requires root privileges.")
        sys.exit(1)
    
    bridge = SilentBridge(sys.argv[1], sys.argv[2])
    bridge.run()
