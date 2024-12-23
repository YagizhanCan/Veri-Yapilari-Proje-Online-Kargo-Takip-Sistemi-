import heapq

class ShipmentNode:
    """
    Gönderi düğümü:
    Parametreler:
    - shipment_id: Kargo ID (int)
    - date: Gönderi tarihi (int veya YYYYMMDD formatında)
    - status: "Teslim Edildi" / "Teslim Edilmedi"
    - delivery_time: Teslim süresi (gün cinsinden, int)
    next: Sonraki gönderi düğümü.
    """
    def __init__(self, shipment_id, date, status, delivery_time):
        self.shipment_id = shipment_id
        self.date = date
        self.status = status
        self.delivery_time = delivery_time
        self.next = None

class ShipmentLinkedList:
    """
    Müşteriye ait gönderi geçmişini tutan linked list.
    Gönderiler tarih sırasına göre eklenir.
    """
    def __init__(self):
        self.head = None
    
    def insert_sorted(self, shipment_id, date, status, delivery_time):
        """
        Tarihe göre sıralı ekleme yapar. 
        Yeni gönderi, tarih değeri küçük olan başa veya uygun yere eklenir.
        Zaman Karmaşıklığı: O(n) (liste uzunluğuna göre)
        """
        new_node = ShipmentNode(shipment_id, date, status, delivery_time)
        if self.head is None or date < self.head.date:
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            while current.next is not None and current.next.date < date:
                current = current.next
            new_node.next = current.next
            current.next = new_node
    
    def display(self):
        """
        Tüm gönderileri ekrana basar.
        """
        current = self.head
        if current is None:
            print("Gönderim geçmişi boş.")
            return
        while current:
            print(f"Kargo ID: {current.shipment_id}, Tarih: {current.date}, "
                  f"Durum: {current.status}, Süre: {current.delivery_time} gün")
            current = current.next

    def get_all_shipments(self):
        """
        Tüm gönderileri bir liste olarak döndürür.
        Format: [(shipment_id, date, status, delivery_time), ...]
        """
        shipments = []
        current = self.head
        while current:
            shipments.append((current.shipment_id, current.date, current.status, current.delivery_time))
            current = current.next
        return shipments

class CustomerNode:
    """
    Müşteri düğümü:
    Parametreler:
    - customer_id: int
    - name: str
    - surname: str
    - shipment_history: Müşterinin gönderi geçmişi (ShipmentLinkedList)
    - last_shipments_stack: Son 5 gönderiyi tutan bir stack (list)
    """
    def __init__(self, customer_id, name, surname):
        self.customer_id = customer_id
        self.name = name
        self.surname = surname
        self.shipment_history = ShipmentLinkedList()
        self.last_shipments_stack = []
        self.next = None

    def push_last_shipment(self, shipment):
        """
        Yeni gönderi eklendiğinde son 5 gönderiyi tutan stack'e push yapar.
        Stack LIFO mantığında, en son eklenen en üstte.
        Eğer 5'ten fazla olmaya başlarsa en eskisini çıkarır.
        """
        self.last_shipments_stack.append(shipment)
        if len(self.last_shipments_stack) > 5:
            self.last_shipments_stack.pop(0)

    def display_last_shipments(self):
        """
        Son 5 (veya daha az) gönderiyi ekrana basar.
        Stack boş ise hata mesajı verir.
        """
        if not self.last_shipments_stack:
            print("Bu müşterinin gönderim geçmişi boş.")
        else:
            print(f"Müşteri ID: {self.customer_id} - Son Gönderiler:")
            for sh in reversed(self.last_shipments_stack):
                print(f"Kargo ID: {sh[0]}, Tarih: {sh[1]}, Durum: {sh[2]}, Süre: {sh[3]}")

class CustomerLinkedList:
    """
    Tüm müşterilerin tutulduğu linked list.
    Müşteri ekleme: Başa ekleme veya ID kontrolünden sonra yapılır.
    """
    def __init__(self):
        self.head = None

    def add_customer(self, customer_id, name, surname):
        """
        Yeni müşteri ekler. ID benzersiz olmalı.
        Zaman Karmaşıklığı: O(n) (müşteri bulmak için)
        """
        if self.find_customer(customer_id):
            print("Bu müşteri ID zaten mevcut!")
            return
        new_customer = CustomerNode(customer_id, name, surname)
        new_customer.next = self.head
        self.head = new_customer

    def find_customer(self, customer_id):
        """
        Müşteri ID'ye göre arama.
        Zaman Karmaşıklığı: O(n)
        """
        current = self.head
        while current:
            if current.customer_id == customer_id:
                return current
            current = current.next
        return None

    def display_all_customers(self):
        """
        Tüm müşterileri listeler.
        """
        current = self.head
        if current is None:
            print("Sistemde müşteri bulunmuyor.")
            return
        while current:
            print(f"Müşteri ID: {current.customer_id}, İsim: {current.name} {current.surname}")
            current = current.next

# --------------------------------------------
# 2. Kargo Önceliklendirme (Priority Queue)
# --------------------------------------------
# Teslim süresi düşük olan kargolar öncelikli.
# Python'da heapq min-heap olarak kullanılır.
# Format: (delivery_time, shipment_id, status)
# --------------------------------------------
# Zaman karmaşıklığı:
# Ekleme: O(log n)
# Çıkarma: O(log n)
# --------------------------------------------
class CargoPriorityQueue:
    def __init__(self):
        self.heap = []
    
    def add_cargo(self, shipment_id, delivery_time, status):
        """
        Öncelik sırasına göre heap'e ekler.
        delivery_time öncelik kriteri.
        """
        heapq.heappush(self.heap, (delivery_time, shipment_id, status))
    
    def pop_cargo(self):
        """
        Öncelikli kargoyu çeker.
        """
        if not self.heap:
            return None
        return heapq.heappop(self.heap)

    def display_all(self):
        """
        Tüm kargoları öncelik sırasına göre görüntüler (heap'i bozmadan).
        """
        print("Öncelikli kargolar (teslim süresine göre artan):")
        temp = sorted(self.heap, key=lambda x: x[0])
        if not temp:
            print("Öncelikli kargo bulunmuyor.")
        for item in temp:
            print(f"Kargo ID: {item[1]}, Süre: {item[0]} gün, Durum: {item[2]}")

# --------------------------------------------
# 3. Kargo Rotalama (Tree)
# --------------------------------------------
# Ağaç yapısı: Kök Merkez, çocuklar alt şehirler.
# En kısa rota: en az derinliğe sahip yapraka ulaşma mesafesi.
# Ağaç derinliği BFS ile bulunarak en kısa derinlik hesaplanır.

class CityNode:
    """
    Şehir düğümü:
    - city_id
    - city_name
    - children: alt şehirler (liste)
    """
    def __init__(self, city_id, city_name):
        self.city_id = city_id
        self.city_name = city_name
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

def print_tree(root, level=0):
    """
    Ağacı konsola hiyerarşik şekilde yazdırır.
    """
    print("    " * level + f"{root.city_name} (ID: {root.city_id})")
    for child in root.children:
        print_tree(child, level+1)

def shortest_route_depth(root):
    """
    En kısa rota derinliğini BFS ile bulur.
    Bu derinlik, en kısa teslimat süresi olarak değerlendirilebilir.
    Zaman Karmaşıklığı: O(n) n = düğüm sayısı
    """
    from collections import deque
    q = deque([(root, 1)])
    while q:
        node, depth = q.popleft()
        if not node.children:
            return depth
        for c in node.children:
            q.append((c, depth+1))
    return 1

# --------------------------------------------
# 4. Gönderim Geçmişi Sorgulama (Stack)
# --------------------------------------------
# Her müşterinin last_shipments_stack özelliği ile son 5 gönderi.

# --------------------------------------------
# 5. Kargo Durum Sorgulama (Sorting & Searching)
# --------------------------------------------
# Teslim Edilmiş Kargolar: Kargo ID'ye göre binary search
# Teslim Edilmemiş Kargolar: Teslim süresine göre merge sort

def binary_search_delivered(arr, target_id):
    """
    Teslim edilmiş kargolar arasında binary search.
    arr sorted by shipment_id
    Zaman karmaşıklığı: O(log n)
    """
    low, high = 0, len(arr)-1
    while low <= high:
        mid = (low+high)//2
        if arr[mid][0] == target_id:
            return arr[mid]
        elif arr[mid][0] < target_id:
            low = mid+1
        else:
            high = mid-1
    return None

def merge_sort_shipments(arr):
    """
    Teslim edilmemiş kargoları teslim süresine göre merge sort ile sıralar.
    Zaman karmaşıklığı: O(n log n)
    """
    if len(arr) > 1:
        mid = len(arr)//2
        left = arr[:mid]
        right = arr[mid:]
        merge_sort_shipments(left)
        merge_sort_shipments(right)
        
        i=j=k=0
        while i<len(left) and j<len(right):
            if left[i][3] < right[j][3]: # delivery_time'a göre
                arr[k] = left[i]
                i+=1
            else:
                arr[k] = right[j]
                j+=1
            k+=1
        while i<len(left):
            arr[k]=left[i]
            i+=1
            k+=1
        while j<len(right):
            arr[k]=right[j]
            j+=1
            k+=1

# --------------------------------------------
# 6. Raporlama ve Performans Analizi
# --------------------------------------------
# Seçilen Veri Yapıları ve Algoritmalar Hakkında (özet):
# - Linked List: Müşteri ve gönderi geçmişi yönetimi için kullanıldı. 
#   Sıralı ekleme kolaylığı, basitlik. Dezavantaj: O(n) arama/ekleme ortalama.
# - Priority Queue (Min-Heap): Kargoların öncelikli işlenmesi O(log n) ekleme/çıkarma.
# - Tree: Rota yapısı, hiyerarşik şehir yapısı. BFS ile en kısa derinlik O(n).
# - Stack: Son 5 gönderi sorgusu O(1) ekleme/silme.
# - Merge Sort: Teslim edilmemiş kargolar için O(n log n) sıralama.
# - Binary Search: Teslim edilmiş kargolar arasında O(log n) arama.

# --------------------------------------------
# 7. Arayüz (Menü)
# --------------------------------------------
# Konsol tabanlı menü ile fonksiyonlar test edilebilir.

class CargoSystem:
    def __init__(self):
        self.customers = CustomerLinkedList()
        self.priority_queue = CargoPriorityQueue()
        # Teslim edilmiş kargolar listesi (ID, date, status, delivery_time)
        self.delivered_shipments = []
        # Teslim edilmemiş kargolar listesi
        self.undelivered_shipments = []
        
        # Örnek ağaç yapısı oluşturma
        self.root_city = CityNode(0, "Merkez")
        c1 = CityNode(1, "İstanbul")
        c2 = CityNode(2, "Ankara")
        c3 = CityNode(3, "İzmir")
        c4 = CityNode(4, "Bursa")
        self.root_city.add_child(c1)
        self.root_city.add_child(c2)
        c2.add_child(c3)
        c3.add_child(c4)

    def add_customer(self):
        cid = int(input("Müşteri ID: "))
        name = input("İsim: ")
        surname = input("Soyisim: ")
        self.customers.add_customer(cid, name, surname)
        print("Müşteri eklendi!")

    def add_shipment_to_customer(self):
        cid = int(input("Müşteri ID: "))
        customer = self.customers.find_customer(cid)
        if not customer:
            print("Müşteri bulunamadı!")
            return
        shipment_id = int(input("Gönderi ID: "))
        date = int(input("Gönderi tarihi (YYYYMMDD formatında, örn: 20240101): "))
        status = input("Durum (Teslim Edildi/Teslim Edilmedi): ")
        delivery_time = int(input("Teslim süresi (gün): "))

        # Gönderi ekle
        customer.shipment_history.insert_sorted(shipment_id, date, status, delivery_time)
        # Stack'e push
        customer.push_last_shipment((shipment_id, date, status, delivery_time))

        # Priority Queue'ya ekle (Sadece teslim edilmemiş ise)
        if status != "Teslim Edildi":
            self.priority_queue.add_cargo(shipment_id, delivery_time, "İşleme Alındı")
            self.undelivered_shipments.append((shipment_id, date, status, delivery_time))
        else:
            self.delivered_shipments.append((shipment_id, date, status, delivery_time))

        print("Gönderi eklendi!")

    def query_shipment_history(self):
        cid = int(input("Müşteri ID: "))
        customer = self.customers.find_customer(cid)
        if not customer:
            print("Müşteri bulunamadı!")
            return
        print("Gönderim Geçmişi (Tarih Sırasına Göre):")
        customer.shipment_history.display()

    def query_last_five_shipments(self):
        cid = int(input("Müşteri ID: "))
        customer = self.customers.find_customer(cid)
        if not customer:
            print("Müşteri bulunamadı!")
            return
        customer.display_last_shipments()

    def list_all_cargos_sorted(self):
        """
        Tüm kargoları listeler:
        - Teslim edilmiş kargolar: Kargo ID'ye göre sıralanıp gösterilir.
        - Teslim edilmemiş kargolar: Teslim süresine göre merge sort ile sıralanır.
        """
        delivered_sorted = sorted(self.delivered_shipments, key=lambda x: x[0])
        undelivered_copy = self.undelivered_shipments[:]
        merge_sort_shipments(undelivered_copy)

        print("=== Teslim Edilmiş Kargolar (ID'ye göre sıralı) ===")
        if not delivered_sorted:
            print("Teslim edilmiş kargo yok.")
        for sh in delivered_sorted:
            print(f"ID: {sh[0]}, Tarih: {sh[1]}, Durum: {sh[2]}, Süre: {sh[3]}")

        print("=== Teslim Edilmemiş Kargolar (Teslim Süresine göre sıralı) ===")
        if not undelivered_copy:
            print("Teslim edilmemiş kargo yok.")
        for sh in undelivered_copy:
            print(f"ID: {sh[0]}, Tarih: {sh[1]}, Durum: {sh[2]}, Süre: {sh[3]}")

    def search_delivered_cargo_by_id(self):
        """
        Teslim edilmiş kargolar arasında binary search.
        Kullanıcı kargo ID girer, teslim edilmiş listede aranır.
        """
        target = int(input("Aranacak Kargo ID: "))
        delivered_sorted = sorted(self.delivered_shipments, key=lambda x: x[0])
        result = binary_search_delivered(delivered_sorted, target)
        if result:
            print(f"BULUNDU: ID: {result[0]}, Tarih: {result[1]}, Durum: {result[2]}, Süre: {result[3]} gün")
        else:
            print("Bu ID'ye sahip teslim edilmiş kargo bulunamadı.")

    def show_delivery_routes(self):
        """
        Ağaç yapısını gösterir ve en kısa rota derinliğini hesaplar.
        """
        print("=== Teslimat Rotası Ağaç Yapısı ===")
        print_tree(self.root_city)
        shortest = shortest_route_depth(self.root_city)
        print(f"En kısa rota derinliği: {shortest}")
        # İsterseniz bu derinliği bir teslimat süresi olarak da yorumlayabilirsiniz.

    def show_priority_queue(self):
        self.priority_queue.display_all()

def main():
    system = CargoSystem()

    while True:
        print("\n=== ONLINE KARGO TAKİP SİSTEMİ ===")
        print("1. Yeni müşteri ekle")
        print("2. Kargo gönderimi ekle")
        print("3. Kargo durumu sorgula (teslim edilmiş kargoda binary search)")
        print("4. Gönderim geçmişini görüntüle (müşteri bazlı)")
        print("5. Tüm kargoları listele (sıralı)")
        print("6. Teslimat rotalarını göster (ağaç)")
        print("7. Bir müşterinin son 5 gönderisini göster (stack)")
        print("8. Öncelikli kargoları görüntüle (Priority Queue)")
        print("9. Çıkış")

        choice = input("Seçiminiz: ")

        if choice == '1':
            system.add_customer()
        elif choice == '2':
            system.add_shipment_to_customer()
        elif choice == '3':
            system.search_delivered_cargo_by_id()
        elif choice == '4':
            system.query_shipment_history()
        elif choice == '5':
            system.list_all_cargos_sorted()
        elif choice == '6':
            system.show_delivery_routes()
        elif choice == '7':
            system.query_last_five_shipments()
        elif choice == '8':
            system.show_priority_queue()
        elif choice == '9':
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen 1-9 arasında bir değer girin.")

if __name__ == "__main__":
    main()
