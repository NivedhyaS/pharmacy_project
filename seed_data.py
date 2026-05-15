import os
import django
import random
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from drugs.models import Drug, Category, Batch
from suppliers.models import Supplier
from billing.models import Bill, BillItem
from django.contrib.auth.models import User

def seed_data():
    # 1. Categories
    categories_data = [
        ('Painkillers', 'Medicines for pain relief'),
        ('Antibiotics', 'Medicines to treat bacterial infections'),
        ('Antipyretics', 'Medicines to reduce fever'),
        ('Antivirals', 'Medicines for viral infections'),
        ('Vitamins', 'Nutritional supplements'),
        ('Syrups', 'Liquid medications')
    ]
    
    for name, desc in categories_data:
        Category.objects.get_or_create(name=name, defaults={'description': desc})
    
    all_cats = list(Category.objects.all())
    print(f"Categories: {len(all_cats)}")

    # 2. Suppliers
    suppliers_data = [
        ('MedLife Pharma', 'John Doe', '9876543210', 'medlife@example.com', 'Mumbai, India'),
        ('Global Healthcare', 'Jane Smith', '9876543211', 'global@example.com', 'Delhi, India'),
        ('Astra Distributors', 'Mike Ross', '9876543212', 'astra@example.com', 'Bangalore, India'),
        ('Alpha Medicals', 'Sarah Connor', '9876543213', 'alpha@example.com', 'Chennai, India'),
        ('Wellness Pharma', 'Peter Parker', '9876543214', 'wellness@example.com', 'Kolkata, India')
    ]
    
    for name, cp, phone, email, addr in suppliers_data:
        Supplier.objects.get_or_create(
            name=name, 
            defaults={
                'contact_person': cp,
                'phone': phone,
                'email': email,
                'address': addr,
                'gst_number': f'27AAAAA{random.randint(1000, 9999)}A1Z5'
            }
        )
    print(f"Suppliers: {Supplier.objects.count()}")

    # 3. Drugs
    drugs_data = [
        ('Paracetamol', 'Dolo', 'Paracetamol 500mg', random.choice(all_cats), 'tablet'),
        ('Amoxicillin', 'Mox', 'Amoxicillin 250mg', random.choice(all_cats), 'capsule'),
        ('Cough Relief', 'Benadryl', 'Diphenhydramine', random.choice(all_cats), 'syrup'),
        ('Vitamin C', 'Limcee', 'Ascorbic Acid 500mg', random.choice(all_cats), 'tablet'),
        ('Insulin', 'Humalog', 'Insulin Lispro', random.choice(all_cats), 'injection'),
        ('Aspirin', 'Ecosprin', 'Acetylsalicylic acid', random.choice(all_cats), 'tablet')
    ]

    for name, brand, comp, cat, unit in drugs_data:
        Drug.objects.get_or_create(
            name=name,
            brand=brand,
            defaults={
                'composition': comp,
                'category': cat,
                'unit': unit,
                'hsn_code': f'300{random.randint(10, 99)}',
                'rack_number': f'R-{random.randint(1, 5)}',
                'min_stock': 10
            }
        )
    print(f"Drugs: {Drug.objects.count()}")

    # 4. Batches
    all_drugs = list(Drug.objects.all())
    for drug in all_drugs:
        # Check if drug already has batches
        if drug.batches.count() < 1:
            # Create a batch
            Batch.objects.create(
                drug=drug,
                batch_number=f'BTCH{random.randint(1000, 9999)}',
                manufacture_date=date.today() - timedelta(days=random.randint(30, 365)),
                expiry_date=date.today() + timedelta(days=random.randint(180, 730)),
                quantity=random.randint(50, 500),
                purchase_price=random.randint(5, 50),
                selling_price=random.randint(60, 100)
            )
    print(f"Batches: {Batch.objects.count()}")

    # 5. Bills
    if Bill.objects.count() < 5:
        user = User.objects.first()
        patients = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
        batches = list(Batch.objects.filter(quantity__gt=10))
        
        for i in range(5):
            bill = Bill.objects.create(
                bill_number=f'B{random.randint(10000, 99999)}',
                patient_name=random.choice(patients),
                doctor_name='Dr. Smith',
                cashier=user,
                payment_mode=random.choice(['cash', 'upi']),
            )
            
            # Add 2 items per bill
            bill_total = 0
            for _ in range(2):
                batch = random.choice(batches)
                qty = random.randint(1, 5)
                item = BillItem.objects.create(
                    bill=bill,
                    drug=batch.drug,
                    batch=batch,
                    quantity=qty,
                    selling_price=batch.selling_price,
                    gst_percent=12
                )
                bill_total += item.total
            
            bill.total_amount = bill_total
            bill.save()
    print(f"Bills: {Bill.objects.count()}")

if __name__ == '__main__':
    seed_data()
