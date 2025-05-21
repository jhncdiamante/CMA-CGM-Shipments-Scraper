class ShipmentError(Exception):
    """Base exception class for shipment-related errors."""
    pass


class ContainerNotFoundError(ShipmentError):
    """Raised when a container cannot be found in the shipment."""
    def __init__(self, shipment_id: str, message: str = None):
        self.shipment_id = shipment_id
        self.message = message or f"No containers found for shipment {shipment_id}"
        super().__init__(self.message)

class ShipmentTimeoutError(ShipmentError):
    """Raised when operations on a shipment timeout."""
    def __init__(self, shipment_id: str, operation: str, message: str = None):
        self.shipment_id = shipment_id
        self.operation = operation
        self.message = message or f"Operation '{operation}' timed out for shipment {shipment_id}"
        super().__init__(self.message)



class ElementNotFoundError(Exception):
    '''Base exception class for web objects related errors.'''
    pass

class ButtonNotFoundError(ElementNotFoundError):
    '''Raised when finding or locating the search button leads to timeout.'''
    def __init__(self, identifier: str, message: str = None):
        self.id = identifier
        self.message = message or f"Failed to locate or find button with identifier: {self.id}"
        super().__init__(self.message) 