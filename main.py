import PySimpleGUI as sg
import heapq
from collections import deque

##############################################################################
#                           GENEL AYARLAR
##############################################################################

# Genel tema
sg.theme('DarkBlue14')

# Genel font
GENEL_FONT = ("Verdana", 14, "bold")
# Karmaşıklık ASCII grafikleri için monospaced font
POPUP_FONT = ("Courier New", 12)

##############################################################################
#                   ZAMAN KARMAŞIKLIĞI GÖRSELLEŞTİRME
##############################################################################

def print_complexity(choice):
    """
    Her menü seçeneği (ve eklediğimiz yeni metodlar) için ilgili işlem bittikten sonra 
    zaman karmaşıklığı bilgisini ve basit bir ASCII 'graph' gösterir.
    """
    complexity_map = {
        '1':  ("O(n)",       "****"),
        '2':  ("O(n)",       "****"),
        '3':  ("O(log n)",   "**"),
        '4':  ("O(n)",       "****"),
        '5':  ("O(n log n)", "******"),
        '6':  ("O(n)",       "****"),
        '7':  ("O(1)",       "*"),
        '8':  ("O(n)",       "****"),
        '9':  ("O(n)",       "****"),
        '10': ("O(n)",       "****"),
        '11': ("O(n)",       "****"),
        '12': ("O(n)",       "****"),
        '13': ("O(n log n)", "******"),
        '14': ("O(n)",       "****"),
        '15': ("O(n)",       "****"),
        '16': ("O(n)",       "****"),
        '17': ("O(n)",       "****"),
        '18': ("O(n)",       "****"),
        '19': ("O(n)",       "****"),
        # 20 => Çıkış (buna O(1) denilebilir)
        # 21 => İşlem Geçmişi (buna da O(n) denilebilir)
        '21': ("O(n)",       "****"),
    }
    if choice in complexity_map:
        comp_str, graph = complexity_map[choice]
        ascii_graph = " ".join(list(graph))
        message = (
            f"Bu işlem: {comp_str}\n\n"
            f"Karmaşıklık Grafiği (Sembolik):\n"
            f"  {ascii_graph}"
        )
        sg.popup_scrolled(
            message,
            title="Zaman Karmaşıklığı",
            font=POPUP_FONT,
            size=(50, 8)
        )

##############################################################################
#                           VERİ YAPISI SINIFLARI
##############################################################################

class ShipmentNode:
    def __init__(self, shipment_id, date, status, delivery_time):
        self.shipment_id = shipment_id
        self.date = date
        self.status = status
        self.delivery_time = delivery_time
        self.next = None

class ShipmentLinkedList:
    def __init__(self):
        self.head = None

    def insert_sorted(self, shipment_id, date, status, delivery_time):
        """
        Yeni gönderiyi tarih bazında sıralı ekler (O(n))
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
        Tüm gönderileri ekrana basar (O(n))
        """
        current = self.head
        if current is None:
            sg.popup("Gönderim geçmişi boş.", title="Gönderim Geçmişi", font=GENEL_FONT)
            return
        message = []
        while current:
            msg = (
                f"Kargo ID: {current.shipment_id}, Tarih: {current.date}, "
                f"Durum: {current.status}, Süre: {current.delivery_time} gün"
            )
            message.append(msg)
            current = current.next
        sg.popup_scrolled("\n".join(message), title="Gönderim Geçmişi", font=GENEL_FONT)

    def get_all_shipments(self):
        """
        Tüm gönderileri liste olarak döndürür (O(n))
        """
        shipments = []
        current = self.head
        while current:
            shipments.append((current.shipment_id, current.date, current.status, current.delivery_time))
            current = current.next
        return shipments

class CustomerNode:
    def __init__(self, customer_id, name, surname):
        self.customer_id = customer_id
        self.name = name
        self.surname = surname
        self.shipment_history = ShipmentLinkedList()
        self.last_shipments_stack = []
        self.next = None

    def push_last_shipment(self, shipment):
        """
        Son 5 gönderiyi stack (liste) mantığıyla tutar.
        """
        self.last_shipments_stack.append(shipment)
        if len(self.last_shipments_stack) > 5:
            self.last_shipments_stack.pop(0)

    def display_last_shipments(self):
        """
        Son 5 gönderiyi ters sırada gösterir (stack).
        """
        if not self.last_shipments_stack:
            sg.popup(
                "Bu müşterinin gönderim geçmişi boş.",
                title="Son Gönderiler",
                font=GENEL_FONT
            )
            return
        lines = []
        for sh in reversed(self.last_shipments_stack):
            lines.append(
                f"Kargo ID: {sh[0]}, Tarih: {sh[1]}, Durum: {sh[2]}, Süre: {sh[3]}"
            )
        sg.popup_scrolled("\n".join(lines), title="Son Gönderiler", font=GENEL_FONT)

class CustomerLinkedList:
    def __init__(self):
        self.head = None

    def add_customer(self, customer_id, name, surname):
        """
        Müşteri eklemeden önce ID var mı diye kontrol ediyoruz (O(n))
        """
        if self.find_customer(customer_id):
            sg.popup("Bu müşteri ID zaten mevcut!", title="Hata", font=GENEL_FONT)
            return
        new_customer = CustomerNode(customer_id, name, surname)
        new_customer.next = self.head
        self.head = new_customer

    def find_customer(self, customer_id):
        """
        ID'ye göre müşteri aramak (O(n))
        """
        current = self.head
        while current:
            if current.customer_id == customer_id:
                return current
            current = current.next
        return None

    def remove_customer(self, customer_id):
        """
        Bağlı listeden müşteri silmek (O(n))
        """
        current = self.head
        prev = None
        while current:
            if current.customer_id == customer_id:
                if prev is None:
                    self.head = current.next
                else:
                    prev.next = current.next
                sg.popup(
                    f"Müşteri {customer_id} silindi.",
                    title="Silme Başarılı",
                    font=GENEL_FONT
                )
                return
            prev = current
            current = current.next
        sg.popup("Müşteri bulunamadı, silinemedi.", title="Hata", font=GENEL_FONT)

    def get_all_customers(self):
        """
        Tüm müşteri düğümlerini listeye atıp döndürür (O(n))
        """
        customers = []
        current = self.head
        while current:
            customers.append(current)
            current = current.next
        return customers

    def display_all_customers(self):
        """
        Tüm müşterileri ekrana basar (O(n))
        """
        current = self.head
        if current is None:
            sg.popup(
                "Sistemde müşteri bulunmuyor.",
                title="Müşteriler",
                font=GENEL_FONT
            )
            return
        lines = []
        while current:
            msg = f"Müşteri ID: {current.customer_id}, İsim: {current.name} {current.surname}"
            lines.append(msg)
            current = current.next
        sg.popup_scrolled("\n".join(lines), title="Müşteriler", font=GENEL_FONT)

class CargoPriorityQueue:
    def __init__(self):
        self.heap = []

    def add_cargo(self, shipment_id, delivery_time, status):
        """
        Heap kullanarak O(log n) ekleme
        """
        heapq.heappush(self.heap, (delivery_time, shipment_id, status))

    def pop_cargo(self):
        if not self.heap:
            return None
        return heapq.heappop(self.heap)

    def remove_cargo_by_id(self, shipment_id):
        """
        Heap içinde ID arayarak silme (O(n))
        """
        removed = False
        temp = []
        while self.heap:
            item = heapq.heappop(self.heap)
            if item[1] == shipment_id:
                removed = True
            else:
                temp.append(item)
        for t in temp:
            heapq.heappush(self.heap, t)
        return removed

    def display_all(self):
        """
        Heap'teki tüm kargoları teslim süresine göre artan sırada göster
        """
        temp = sorted(self.heap, key=lambda x: x[0])
        if not temp:
            sg.popup("Öncelikli kargo bulunmuyor.", title="Priority Queue", font=GENEL_FONT)
            return
        lines = []
        for item in temp:
            lines.append(f"Kargo ID: {item[1]}, Süre: {item[0]} gün, Durum: {item[2]}")
        sg.popup_scrolled("\n".join(lines), title="Priority Queue", font=GENEL_FONT)

class CityNode:
    def __init__(self, city_id, city_name):
        self.city_id = city_id
        self.city_name = city_name
        self.children = []

    def add_child(self, child_node):
        """
        Bir şehri diğerinin altına ekler (O(1))
        """
        self.children.append(child_node)

def print_tree(root, level=0, lines=None):
    """
    Ağaçtaki düğümleri hiyerarşik biçimde yazdırır (O(n))
    """
    if lines is None:
        lines = []
    lines.append("    " * level + f"{root.city_name} (ID: {root.city_id})")
    for child in root.children:
        print_tree(child, level+1, lines)
    return lines

def shortest_route_depth(root):
    """
    BFS ile ağacın en kısa rota derinliğini bulur (O(n))
    """
    q = deque([(root, 1)])
    while q:
        node, depth = q.popleft()
        if not node.children:
            return depth
        for c in node.children:
            q.append((c, depth+1))
    return 1

def binary_search_delivered(arr, target_id):
    """
    ID'ye göre sıralanmış teslim edilmiş kargolar listesinde binary search (O(log n))
    """
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid][0] == target_id:
            return arr[mid]
        elif arr[mid][0] < target_id:
            low = mid + 1
        else:
            high = mid - 1
    return None

def merge_sort_shipments(arr):
    """
    Teslim edilmemiş kargoları teslim süresine göre merge sort (O(n log n))
    """
    if len(arr) > 1:
        mid = len(arr)//2
        left = arr[:mid]
        right = arr[mid:]
        merge_sort_shipments(left)
        merge_sort_shipments(right)
        i = j = k = 0
        while i < len(left) and j < len(right):
            if left[i][3] < right[j][3]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

##############################################################################
#                          CARGO SYSTEM SINIFI
##############################################################################

class CargoSystem:
    def __init__(self):
        self.customers = CustomerLinkedList()
        self.priority_queue = CargoPriorityQueue()
        self.delivered_shipments = []
        self.undelivered_shipments = []
        self.transaction_history = []
        self.root_city = CityNode(0, "Merkez")
        c1 = CityNode(1, "İstanbul")
        c2 = CityNode(2, "Ankara")
        c3 = CityNode(3, "İzmir")
        c4 = CityNode(4, "Bursa")
        self.root_city.add_child(c1)
        self.root_city.add_child(c2)
        c2.add_child(c3)
        c3.add_child(c4)

    def add_history(self, message):
        """
        İşlem geçmişine yeni bir kayıt ekler.
        """
        self.transaction_history.append(message)

    def show_history(self):
        """
        Tüm işlem geçmişini GUI'de gösterir.
        """
        if not self.transaction_history:
            sg.popup("Henüz herhangi bir işlem yapılmadı.", title="İşlem Geçmişi")
            print_complexity('21')
            return
        lines = []
        for idx, h in enumerate(self.transaction_history, start=1):
            lines.append(f"{idx}. {h}")
        sg.popup_scrolled("\n".join(lines), title="İşlem Geçmişi")
        print_complexity('21')

    def add_customer(self):
        layout = [
            [sg.Text("Müşteri ID: "), sg.Input(key="cid")],
            [sg.Text("İsim: "), sg.Input(key="name")],
            [sg.Text("Soyisim: "), sg.Input(key="surname")],
            [sg.Button("Kaydet"), sg.Button("İptal")]
        ]
        window = sg.Window("Yeni Müşteri Ekle", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "İptal"):
                break
            if event == "Kaydet":
                try:
                    cid = int(values["cid"])
                    name = values["name"]
                    surname = values["surname"]
                    self.customers.add_customer(cid, name, surname)
                    sg.popup("Müşteri eklendi!", title="Başarılı", font=GENEL_FONT)
                    self.add_history(f"Müşteri eklendi (ID={cid}, İsim={name}, Soyisim={surname})")
                    print_complexity('1')
                except ValueError:
                    sg.popup("Lütfen geçerli bir ID giriniz!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def add_shipment_to_customer(self):
        layout = [
            [sg.Text("Müşteri ID: "), sg.Input(key="cid")],
            [sg.Text("Gönderi ID: "), sg.Input(key="shipment_id")],
            [sg.Text("Gönderi Tarihi (YYYYMMDD): "), sg.Input(key="date")],
            [sg.Text("Durum: (Teslim Edildi/Teslim Edilmedi)"), sg.Input(key="status")],
            [sg.Text("Teslim süresi (gün): "), sg.Input(key="delivery_time")],
            [sg.Button("Ekle"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Kargo Gönderimi Ekle", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Ekle":
                try:
                    cid = int(values["cid"])
                    shipment_id = int(values["shipment_id"])
                    date = int(values["date"])
                    status = values["status"]
                    delivery_time = int(values["delivery_time"])
                    customer = self.customers.find_customer(cid)
                    if not customer:
                        sg.popup("Müşteri bulunamadı!", title="Hata", font=GENEL_FONT)
                        break
                    customer.shipment_history.insert_sorted(shipment_id, date, status, delivery_time)
                    customer.push_last_shipment((shipment_id, date, status, delivery_time))
                    if status != "Teslim Edildi":
                        self.priority_queue.add_cargo(shipment_id, delivery_time, "İşleme Alındı")
                        self.undelivered_shipments.append((shipment_id, date, status, delivery_time))
                    else:
                        self.delivered_shipments.append((shipment_id, date, status, delivery_time))
                    sg.popup("Gönderi eklendi!", title="Başarılı", font=GENEL_FONT)
                    self.add_history(f"Kargo eklendi (MüşteriID={cid}, KargoID={shipment_id}, Durum={status})")
                    print_complexity('2')
                except ValueError:
                    sg.popup("Lütfen tüm alanları doğru formatta doldurun!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def search_delivered_cargo_by_id(self):
        layout = [
            [sg.Text("Aranacak Kargo ID: "), sg.Input(key="target")],
            [sg.Button("Ara"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Kargo Durumu Sorgula", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Ara":
                try:
                    target = int(values["target"])
                    delivered_sorted = sorted(self.delivered_shipments, key=lambda x: x[0])
                    result = binary_search_delivered(delivered_sorted, target)
                    if result:
                        sg.popup(
                            f"BULUNDU:\n\nID: {result[0]}, Tarih: {result[1]}, Durum: {result[2]}, Süre: {result[3]} gün",
                            title="Sonuç",
                            font=GENEL_FONT
                        )
                        self.add_history(f"Kargo durumu sorgulandı (KargoID={target} - Bulundu)")
                    else:
                        sg.popup(
                            "Bu ID'ye sahip teslim edilmiş kargo bulunamadı.",
                            title="Sonuç",
                            font=GENEL_FONT
                        )
                        self.add_history(f"Kargo durumu sorgulandı (KargoID={target} - Bulunamadı)")
                    print_complexity('3')
                except ValueError:
                    sg.popup("Lütfen geçerli bir kargo ID girin!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def query_shipment_history(self):
        layout = [
            [sg.Text("Müşteri ID: "), sg.Input(key="cid")],
            [sg.Button("Göster"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Gönderim Geçmişini Görüntüle", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Göster":
                try:
                    cid = int(values["cid"])
                    customer = self.customers.find_customer(cid)
                    if not customer:
                        sg.popup("Müşteri bulunamadı!", title="Hata", font=GENEL_FONT)
                        break
                    customer.shipment_history.display()
                    self.add_history(f"Gönderim geçmişi görüntülendi (MüşteriID={cid})")
                    print_complexity('4')
                except ValueError:
                    sg.popup("Lütfen geçerli bir müşteri ID girin!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def list_all_cargos_sorted(self):
        delivered_sorted = sorted(self.delivered_shipments, key=lambda x: x[0])
        undelivered_copy = self.undelivered_shipments[:]
        merge_sort_shipments(undelivered_copy)
        lines = []
        lines.append("=== Teslim Edilmiş Kargolar (ID'ye göre) ===")
        if not delivered_sorted:
            lines.append("Teslim edilmiş kargo yok.")
        else:
            for sh in delivered_sorted:
                lines.append(f"ID: {sh[0]}, Tarih: {sh[1]}, Durum: {sh[2]}, Süre: {sh[3]}")
        lines.append("\n=== Teslim Edilmemiş Kargolar (Teslim Süresine göre) ===")
        if not undelivered_copy:
            lines.append("Teslim edilmemiş kargo yok.")
        else:
            for sh in undelivered_copy:
                lines.append(f"ID: {sh[0]}, Tarih: {sh[1]}, Durum: {sh[2]}, Süre: {sh[3]}")
        sg.popup_scrolled("\n".join(lines), title="Tüm Kargolar", font=GENEL_FONT)
        self.add_history("Tüm kargolar listelendi.")
        print_complexity('5')

    def show_delivery_routes(self):
        lines = print_tree(self.root_city)
        shortest = shortest_route_depth(self.root_city)
        lines.append(f"\nEn kısa rota derinliği: {shortest}")
        sg.popup_scrolled("\n".join(lines), title="Teslimat Rotası (Ağaç)", font=GENEL_FONT)
        self.add_history("Teslimat rotaları görüntülendi.")
        print_complexity('6')

    def query_last_five_shipments(self):
        layout = [
            [sg.Text("Müşteri ID: "), sg.Input(key="cid")],
            [sg.Button("Göster"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Son 5 Gönderiyi Göster", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Göster":
                try:
                    cid = int(values["cid"])
                    customer = self.customers.find_customer(cid)
                    if not customer:
                        sg.popup("Müşteri bulunamadı!", title="Hata", font=GENEL_FONT)
                        break
                    customer.display_last_shipments()
                    self.add_history(f"Son 5 gönderi görüntülendi (MüşteriID={cid})")
                    print_complexity('7')
                except ValueError:
                    sg.popup("Lütfen geçerli bir ID girin!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def show_priority_queue(self):
        self.priority_queue.display_all()
        self.add_history("Öncelikli kargolar (PQ) görüntülendi.")
        print_complexity('8')

    def remove_customer_by_id(self):
        layout = [
            [sg.Text("Silinecek müşteri ID: "), sg.Input(key="cid")],
            [sg.Button("Sil"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Müşteri Sil", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Sil":
                try:
                    cid = int(values["cid"])
                    self.customers.remove_customer(cid)
                    self.add_history(f"Müşteri silindi (ID={cid})")
                    print_complexity('9')
                except ValueError:
                    sg.popup("Lütfen geçerli bir müşteri ID girin!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def deliver_cargo(self):
        layout = [
            [sg.Text("Teslim edilecek kargo ID: "), sg.Input(key="shipment_id")],
            [sg.Button("Teslim Et"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Kargoyu Teslim Et", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Teslim Et":
                try:
                    shipment_id = int(values["shipment_id"])
                    index = -1
                    for i, sh in enumerate(self.undelivered_shipments):
                        if sh[0] == shipment_id:
                            index = i
                            break
                    if index == -1:
                        sg.popup("Bu ID ile teslim edilmemiş kargo bulunamadı.", title="Hata", font=GENEL_FONT)
                        break
                    sh = self.undelivered_shipments.pop(index)
                    removed = self.priority_queue.remove_cargo_by_id(shipment_id)
                    if not removed:
                        sg.popup(
                            "Kargo öncelik kuyruğunda bulunamadı,\n"
                            "ama undelivered list'ten çıkarıldı.",
                            title="Bilgi",
                            font=GENEL_FONT
                        )
                    new_sh = (sh[0], sh[1], "Teslim Edildi", sh[3])
                    self.delivered_shipments.append(new_sh)
                    sg.popup(f"Kargo {shipment_id} teslim edildi.", title="Başarılı", font=GENEL_FONT)
                    self.add_history(f"Kargo teslim edildi (KargoID={shipment_id})")
                    print_complexity('10')
                except ValueError:
                    sg.popup("Lütfen geçerli bir kargo ID girin!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def add_city(self):
        layout = [
            [sg.Text("Hangi şehir ID'nin altına eklenecek? "), sg.Input(key="parent_id")],
            [sg.Text("Yeni şehrin ID: "), sg.Input(key="new_id")],
            [sg.Text("Yeni şehrin adı: "), sg.Input(key="new_name")],
            [sg.Button("Ekle"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Yeni Şehir Ekle", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Ekle":
                try:
                    parent_id = int(values["parent_id"])
                    new_id = int(values["new_id"])
                    new_name = values["new_name"]
                    parent_node = self.find_city_by_id(self.root_city, parent_id)
                    if parent_node:
                        new_node = CityNode(new_id, new_name)
                        parent_node.add_child(new_node)
                        sg.popup(
                            f"{new_name} şehri {parent_node.city_name} altına eklendi.",
                            title="Başarılı",
                            font=GENEL_FONT
                        )
                        self.add_history(f"Yeni şehir eklendi (ParentID={parent_id}, CityID={new_id}, Name={new_name})")
                    else:
                        sg.popup("Belirtilen ID'ye sahip şehir bulunamadı.", title="Hata", font=GENEL_FONT)
                    print_complexity('11')
                except ValueError:
                    sg.popup("Lütfen geçerli değerler giriniz!", title="Hata", font=GENEL_FONT)
                break
        window.close()

    def find_city_by_id(self, root, city_id):
        """
        BFS ile ağaçta city_id değerini arar ve bulursa döndürür (O(n))
        """
        q = deque([root])
        while q:
            node = q.popleft()
            if node.city_id == city_id:
                return node
            for c in node.children:
                q.append(c)
        return None

    def find_longest_delivery_time_delivered(self):
        if not self.delivered_shipments:
            sg.popup("Hiç teslim edilmiş kargo yok.", title="Bilgi", font=GENEL_FONT)
            print_complexity('12')
            return
        max_cargo = max(self.delivered_shipments, key=lambda x: x[3])
        sg.popup(
            f"En uzun teslim süresine sahip teslim edilmiş kargo:\n\n"
            f"ID: {max_cargo[0]}, Tarih: {max_cargo[1]}, Durum: {max_cargo[2]}, Süre: {max_cargo[3]} gün",
            title="Sonuç",
            font=GENEL_FONT
        )
        self.add_history(f"En uzun teslim süreli kargo görüntülendi (KargoID={max_cargo[0]})")
        print_complexity('12')

    def list_customers_by_name(self):
        cust_list = self.customers.get_all_customers()
        cust_list.sort(key=lambda c: c.name)
        if not cust_list:
            sg.popup("Hiç müşteri bulunmuyor.", title="Bilgi", font=GENEL_FONT)
            return
        lines = []
        for c in cust_list:
            lines.append(f"Müşteri ID: {c.customer_id}, İsim: {c.name} {c.surname}")
        sg.popup_scrolled(
            "\n".join(lines),
            title="Müşteriler (İsim Sırasına Göre)",
            font=GENEL_FONT
        )
        self.add_history("Müşteriler isim sırasına göre listelendi.")
        print_complexity('13')

    def search_customer_by_name(self):
        layout = [
            [sg.Text("Aradığınız müşteri ismi: "), sg.Input(key="name")],
            [sg.Button("Ara"), sg.Button("Vazgeç")]
        ]
        window = sg.Window("Müşteri İsmi ile Ara", layout, font=GENEL_FONT)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "Vazgeç"):
                break
            if event == "Ara":
                name = values["name"]
                current = self.customers.head
                found_any = False
                lines = []
                while current:
                    if current.name == name:
                        lines.append(
                            f"Müşteri ID: {current.customer_id}, "
                            f"İsim: {current.name} {current.surname}"
                        )
                        found_any = True
                    current = current.next
                if not found_any:
                    sg.popup("Bu isimde müşteri bulunamadı.", title="Sonuç", font=GENEL_FONT)
                    self.add_history(f"Müşteri ismine göre arama (Name={name}) - Bulunamadı")
                else:
                    sg.popup_scrolled("\n".join(lines), title="Sonuç", font=GENEL_FONT)
                    self.add_history(f"Müşteri ismine göre arama (Name={name}) - Bulundu")
                print_complexity('14')
                break
        window.close()

    def check_undelivered_cargo_count(self):
        count = len(self.undelivered_shipments)
        sg.popup(f"Toplam {count} adet teslim edilmemiş kargo var.", title="Bilgi", font=GENEL_FONT)
        self.add_history(f"Teslim edilmemiş kargo sayısı sorgulandı (Count={count})")
        print_complexity('15')

    def total_shipment_count(self):
        total = len(self.delivered_shipments) + len(self.undelivered_shipments)
        sg.popup(f"Sistemde toplam {total} adet kargo kaydı mevcut.", title="Bilgi", font=GENEL_FONT)
        self.add_history(f"Toplam kargo sayısı sorgulandı (Toplam={total})")
        print_complexity('16')

    def average_delivery_time(self):
        if not self.delivered_shipments:
            sg.popup("Henüz teslim edilmiş kargo yok, ortalama süre hesaplanamıyor.", title="Bilgi", font=GENEL_FONT)
            print_complexity('17')
            return
        total_time = 0
        for sh in self.delivered_shipments:
            total_time += sh[3]
        avg_time = total_time / len(self.delivered_shipments)
        sg.popup(f"Teslim edilmiş kargoların ortalama teslim süresi: {avg_time:.2f} gün", title="Bilgi", font=GENEL_FONT)
        self.add_history(f"Ortalama teslim süresi hesaplandı (Süre={avg_time:.2f})")
        print_complexity('17')

    def get_customer_count(self):
        customers = self.customers.get_all_customers()
        sg.popup(f"Sistemde toplam {len(customers)} müşteri bulunmaktadır.", title="Bilgi", font=GENEL_FONT)
        self.add_history(f"Müşteri sayısı sorgulandı (Toplam={len(customers)})")
        print_complexity('18')

    def clear_undelivered_shipments(self):
        count = len(self.undelivered_shipments)
        for sh in self.undelivered_shipments:
            _ = self.priority_queue.remove_cargo_by_id(sh[0])
        self.undelivered_shipments.clear()
        sg.popup(f"Tüm teslim edilmemiş {count} kargo silindi.", title="Bilgi", font=GENEL_FONT)
        self.add_history(f"Tüm teslim edilmemiş kargolar silindi (Sayı={count})")
        print_complexity('19')

##############################################################################
#                         ANA GUI FONKSİYONU
##############################################################################

def gui_main():
    sg.set_options(font=GENEL_FONT)
    system = CargoSystem()

    menu_def = [
        [
            'Kargo İşlemleri',
            [
                '1. Yeni müşteri ekle',
                '2. Kargo gönderimi ekle',
                '3. Kargo durumu sorgula',
                '4. Gönderim geçmişini görüntüle',
                '5. Tüm kargoları listele',
                '6. Teslimat rotalarını göster',
                '7. Bir müşterinin son 5 gönderisini göster',
                '8. Öncelikli kargoları görüntüle',
                '9. Müşteri sil',
                '10. Kargoyu Teslim Et (ID ile)',
                '11. Ağaç yapısına yeni şehir ekle',
                '12. En uzun teslim süreli teslim edilmiş kargoyu göster',
                '13. Müşterileri isim sırasına göre listele',
                '14. Müşteri ismine göre ara',
                '15. Teslim edilmemiş kargo sayısını göster',
                '16. Toplam kargo sayısını göster',
                '17. Teslim edilmiş kargoların ortalama teslim süresini göster',
                '18. Toplam müşteri sayısını göster',
                '19. Tüm teslim edilmemiş kargoları sil',
                '20. Çıkış',
                '21. İşlem Geçmişi'
            ]
        ]
    ]
    layout = [
        [
            sg.Menu(menu_def, tearoff=False, key='-MENUBAR-')
        ],
        [
            sg.Text(
                "Online Kargo Takip Sistemi",
                size=(50, 1),
                justification='center',
                font=("Verdana", 18, "bold"),
                relief=sg.RELIEF_RIDGE,
                pad=((0, 0), (10, 10))
            )
        ],
        [
            sg.Text("Lütfen yukarıdaki menüden bir işlem seçin.", justification='center')
        ],
        [
            sg.HorizontalSeparator()
        ],
        [
            sg.Text(
                "Bu proje PySimpleGUI ile tasarlandı.",
                justification='center',
                font=("Verdana", 10, "italic")
            )
        ]
    ]
    window = sg.Window("Kargo Takip Sistemi - GUI", layout, size=(900, 400), element_justification='center')
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        if event == '1. Yeni müşteri ekle':
            system.add_customer()
        elif event == '2. Kargo gönderimi ekle':
            system.add_shipment_to_customer()
        elif event == '3. Kargo durumu sorgula':
            system.search_delivered_cargo_by_id()
        elif event == '4. Gönderim geçmişini görüntüle':
            system.query_shipment_history()
        elif event == '5. Tüm kargoları listele':
            system.list_all_cargos_sorted()
        elif event == '6. Teslimat rotalarını göster':
            system.show_delivery_routes()
        elif event == '7. Bir müşterinin son 5 gönderisini göster':
            system.query_last_five_shipments()
        elif event == '8. Öncelikli kargoları görüntüle':
            system.show_priority_queue()
        elif event == '9. Müşteri sil':
            system.remove_customer_by_id()
        elif event == '10. Kargoyu Teslim Et (ID ile)':
            system.deliver_cargo()
        elif event == '11. Ağaç yapısına yeni şehir ekle':
            system.add_city()
        elif event == '12. En uzun teslim süreli teslim edilmiş kargoyu göster':
            system.find_longest_delivery_time_delivered()
        elif event == '13. Müşterileri isim sırasına göre listele':
            system.list_customers_by_name()
        elif event == '14. Müşteri ismine göre ara':
            system.search_customer_by_name()
        elif event == '15. Teslim edilmemiş kargo sayısını göster':
            system.check_undelivered_cargo_count()
        elif event == '16. Toplam kargo sayısını göster':
            system.total_shipment_count()
        elif event == '17. Teslim edilmiş kargoların ortalama teslim süresini göster':
            system.average_delivery_time()
        elif event == '18. Toplam müşteri sayısını göster':
            system.get_customer_count()
        elif event == '19. Tüm teslim edilmemiş kargoları sil':
            system.clear_undelivered_shipments()
        elif event == '20. Çıkış':
            break
        elif event == '21. İşlem Geçmişi':
            system.show_history()
    window.close()

if __name__ == "__main__":
    gui_main()
