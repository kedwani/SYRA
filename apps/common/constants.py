"""
Common constants for SYRA.
"""

# Visibility levels for medical data
VISIBILITY_PUBLIC = 'public'
VISIBILITY_MEDICAL = 'medical'
VISIBILITY_PRIVATE = 'private'

VISIBILITY_CHOICES = [
    (VISIBILITY_PUBLIC, 'Public - Anyone'),
    (VISIBILITY_MEDICAL, 'Medical Personnel Only'),
    (VISIBILITY_PRIVATE, 'Private - Owner Only'),
]

# Severity levels
SEVERITY_MILD = 'mild'
SEVERITY_MODERATE = 'moderate'
SEVERITY_SEVERE = 'severe'
SEVERITY_LIFE_THREATENING = 'life_threatening'

SEVERITY_CHOICES = [
    (SEVERITY_MILD, 'Mild'),
    (SEVERITY_MODERATE, 'Moderate'),
    (SEVERITY_SEVERE, 'Severe'),
    (SEVERITY_LIFE_THREATENING, 'Life Threatening'),
]

# Bracelet status
BRACELET_UNCLAIMED = 'unclaimed'
BRACELET_CLAIMED = 'claimed'
BRACELET_ACTIVE = 'active'
BRACELET_LOST = 'lost'
BRACELET_SUSPENDED = 'suspended'

BRACELET_STATUS_CHOICES = [
    (BRACELET_UNCLAIMED, 'Unclaimed'),
    (BRACELET_CLAIMED, 'Claimed'),
    (BRACELET_ACTIVE, 'Active'),
    (BRACELET_LOST, 'Lost'),
    (BRACELET_SUSPENDED, 'Suspended'),
]

# Order status
ORDER_PENDING = 'pending'
ORDER_PAID = 'paid'
ORDER_PROCESSING = 'processing'
ORDER_SHIPPED = 'shipped'
ORDER_DELIVERED = 'delivered'
ORDER_CANCELLED = 'cancelled'

ORDER_STATUS_CHOICES = [
    (ORDER_PENDING, 'Pending'),
    (ORDER_PAID, 'Paid'),
    (ORDER_PROCESSING, 'Processing'),
    (ORDER_SHIPPED, 'Shipped'),
    (ORDER_DELIVERED, 'Delivered'),
    (ORDER_CANCELLED, 'Cancelled'),
]

# Cache key prefixes
CACHE_EMERGENCY_CRITICAL = 'emergency:critical:'
CACHE_EMERGENCY_EXTENDED = 'emergency:extended:'
CACHE_USER_PROFILE = 'user:profile:'
CACHE_USER_MEDICAL = 'user:medical:'
CACHE_QR_DATA = 'qr:data:'

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# API rate limits
RATE_LIMIT_ANON = '100/m'
RATE_LIMIT_USER = '200/m'
RATE_LIMIT_EMERGENCY = '20/m'

# JWT settings
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100