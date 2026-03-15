"""Email notification utilities for the Store app."""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer.

    Args:
        order: Order instance
    """
    subject = f"Order Confirmation - {order.order_number}"

    # Plain text message
    message = f"""
    Thank you for your order, {order.user.first_name or order.user.username}!
    
    Order Number: {order.order_number}
    Total Amount: EGP {order.total}
    Payment Method: {order.get_payment_method_display()}
    
    Your order is being processed and will be shipped soon.
    
    You can track your order at: {settings.ALLOWED_HOSTS[0]}/store/orders/{order.id}/
    
    Thank you for choosing SYRA!
    """

    # HTML message (optional enhancement)
    html_message = f"""
    <h2>Order Confirmation</h2>
    <p>Thank you for your order, <strong>{order.user.first_name or order.user.username}</strong>!</p>
    
    <h3>Order Details</h3>
    <ul>
        <li><strong>Order Number:</strong> {order.order_number}</li>
        <li><strong>Total Amount:</strong> EGP {order.total}</li>
        <li><strong>Payment Method:</strong> {order.get_payment_method_display()}</li>
        <li><strong>Status:</strong> {order.get_status_display()}</li>
    </ul>
    
    <h3>Shipping Address</h3>
    <p>
        {order.shipping_name}<br>
        {order.shipping_address}<br>
        {order.shipping_city}<br>
        {order.shipping_area}
    </p>
    
    <p>You can track your order at: {settings.ALLOWED_HOSTS[0]}/store/orders/{order.id}/</p>
    
    <p>Thank you for choosing SYRA!</p>
    """

    # Validate email exists before sending
    if not order.user.email:
        print(
            f"Failed to send order confirmation email: No email address for user {order.user.username}"
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=(
                settings.DEFAULT_FROM_EMAIL
                if hasattr(settings, "DEFAULT_FROM_EMAIL")
                else "noreply@syra.com"
            ),
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send order confirmation email: {e}")
        return False


def send_shipping_notification_email(order):
    """
    Send shipping notification when order is shipped.
    """
    subject = f"Your Order {order.order_number} Has Been Shipped!"

    tracking_url = order.get_tracking_url()

    message = f"""
    Your order has been shipped!
    
    Order Number: {order.order_number}
    Carrier: {order.carrier}
    Tracking Number: {order.tracking_number}
    
    {f'Track your package here: {tracking_url}' if tracking_url else ''}
    
    Thank you for choosing SYRA!
    """

    html_message = f"""
    <h2>Order Shipped!</h2>
    <p>Your order <strong>{order.order_number}</strong> has been shipped!</p>
    
    <h3>Tracking Information</h3>
    <ul>
        <li><strong>Carrier:</strong> {order.carrier}</li>
        <li><strong>Tracking Number:</strong> {order.tracking_number}</li>
    </ul>
    
    {f'<p><a href="{tracking_url}">Track your package</a></p>' if tracking_url else ''}
    
    <p>Thank you for choosing SYRA!</p>
    """

    # Validate email exists before sending
    if not order.user.email:
        print(
            f"Failed to send shipping notification: No email for user {order.user.username}"
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=(
                settings.DEFAULT_FROM_EMAIL
                if hasattr(settings, "DEFAULT_FROM_EMAIL")
                else "noreply@syra.com"
            ),
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send shipping notification email: {e}")
        return False


def send_band_activation_email(registration):
    """
    Send band activation instructions when a band is registered.
    """
    user = registration.user
    subject = "Activate Your SYRA Band - Important Instructions"

    activation_url = f"{settings.ALLOWED_HOSTS[0] if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS else 'http://localhost:8000'}/store/bands/{registration.id}/activate/"

    message = f"""
    Thank you for purchasing a SYRA Band!
    
    Your Band: {registration.nickname}
    Order: {registration.order_item.order.order_number}
    
    IMPORTANT: You must activate your band to link it to your medical profile.
    
    Activation Steps:
    1. Visit: {activation_url}
    2. Enter the unique code found on your band
    3. Complete the activation form
    
    Once activated, your band will:
    • Link to your emergency medical profile
    • Be scannable by first responders
    • Allow emergency contacts to be notified
    
    Need help? Contact us at support@syra.com
    
    Thank you for choosing SYRA!
    """

    html_message = f"""
    <h2>Activate Your SYRA Band</h2>
    <p>Thank you for purchasing a SYRA Band, <strong>{user.first_name or user.username}</strong>!</p>
    
    <div style="background: #f5f5f5; padding: 15px; margin: 15px 0;">
        <h3>Band Details</h3>
        <ul>
            <li><strong>Band Name:</strong> {registration.nickname}</li>
            <li><strong>Order Number:</strong> {registration.order_item.order.order_number}</li>
        </ul>
    </div>
    
    <h3>Important: Activate Your Band</h3>
    <p>You must activate your band to link it to your medical profile.</p>
    
    <p><a href="{activation_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none;">Activate Your Band</a></p>
    
    <h3>What Happens After Activation?</h3>
    <ul>
        <li>Your band links to your emergency medical profile</li>
        <li>First responders can scan your band to access your info</li>
        <li>Your emergency contacts will be notified in emergencies</li>
    </ul>
    
    <p>Need help? Contact us at support@syra.com</p>
    
    <p>Thank you for choosing SYRA!</p>
    """

    # Validate email exists before sending
    if not user.email:
        print(
            f"Failed to send band activation email: No email for user {user.username}"
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=(
                settings.DEFAULT_FROM_EMAIL
                if hasattr(settings, "DEFAULT_FROM_EMAIL")
                else "noreply@syra.com"
            ),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send band activation email: {e}")
        return False


def send_delivery_confirmation_email(order):
    """
    Send delivery confirmation when order is delivered.
    """
    subject = f"Your Order {order.order_number} Has Been Delivered"

    message = f"""
    Your order has been delivered!
    
    Order Number: {order.order_number}
    Delivered on: {order.delivered_at}
    
    Thank you for choosing SYRA!
    We hope you enjoy your SYRA Band!
    
    Don't forget to activate your band to link it to your medical profile.
    """

    html_message = f"""
    <h2>Order Delivered!</h2>
    <p>Your order <strong>{order.order_number}</strong> has been delivered!</p>
    
    <p>We hope you enjoy your SYRA Band!</p>
    
    <h3>Don't Forget to Activate!</h3>
    <p>Remember to activate your band to link it to your medical profile.</p>
    
    <p>Thank you for choosing SYRA!</p>
    """

    # Validate email exists before sending
    if not order.user.email:
        print(
            f"Failed to send delivery confirmation: No email for user {order.user.username}"
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=(
                settings.DEFAULT_FROM_EMAIL
                if hasattr(settings, "DEFAULT_FROM_EMAIL")
                else "noreply@syra.com"
            ),
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send delivery confirmation email: {e}")
        return False
