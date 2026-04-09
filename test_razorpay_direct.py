from app import app, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
import razorpay

with app.app_context():
    print(f'Key ID: {RAZORPAY_KEY_ID}')
    print(f'Key Secret: {RAZORPAY_KEY_SECRET[:10]}...')
    
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    
    # Test order creation with minimal data
    try:
        test_order = {
            'amount': 10000,  # 100 rupees in paisa
            'currency': 'INR',
            'receipt': 'test_receipt_123'
        }
        
        response = client.order.create(data=test_order)
        print('✓ Razorpay order created successfully')
        print(f'Order ID: {response["id"]}')
        print(f'Amount: {response["amount"]}')
        print(f'Status: {response["status"]}')
        
    except Exception as e:
        print(f'✗ Razorpay order creation failed: {e}')
        import traceback
        traceback.print_exc()