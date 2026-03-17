import base64
import logging
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

class DataConverter:
    
    @staticmethod
    def to_float(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, bytes):
            try:
                return float(int.from_bytes(value, byteorder='big', signed=True)) / 100.0
            except Exception:
                return float(value.decode('utf-8', errors='replace'))
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass
            try:
                decoded = base64.b64decode(value + '==')
                return int.from_bytes(decoded, byteorder='big', signed=True) / 100.0
            except Exception as e:
                raise ValueError(f"Cannot convert '{value}' to float: {e}")
        raise ValueError(f"Unsupported type for to_float: {type(value)} value={value!r}")

    @staticmethod
    def to_date(value):
        if value is None:
            return None
        if isinstance(value, (date, datetime)):
            return value
        if isinstance(value, int):
            if abs(value) < 100_000:
                return date(1970, 1, 1) + timedelta(days=value)
            return datetime(1970, 1, 1) + timedelta(microseconds=value)
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse date string: '{value}'")
        raise ValueError(f"Unsupported type for to_date: {type(value)} value={value!r}")

class CDCTransformer:
    def transform(self, topic, message_value):
        payload = message_value.get('payload', {})
        after = payload.get('after')
        op = payload.get('op')

        if not after:
            return None, None, None

        op_desc = "CREATED" if op in ('c', 'r') else "UPDATED"
        entity_type = self._get_entity_type(topic)
        transformed_data = self._transform_payload(entity_type, after)
        payload_id = self._get_payload_id(entity_type, after)

        return entity_type, transformed_data, op_desc, payload_id

    def _get_entity_type(self, topic):
        if 'customers' in topic: 
            return 'customer'
        if 'products' in topic: 
            return 'product'
        if 'orders' in topic: 
            return 'order'
        if 'payments' in topic: 
            return 'payment'
        return 'unknown'

    def _get_payload_id(self, entity_type, after):
        id_map = {'customer': 'cid', 'product': 'pid', 'order': 'oid', 'payment': 'payid'}
        return after.get(id_map.get(entity_type))

    def _transform_payload(self, entity_type, after):
        """Performs entity-specific field transformations (like type casting)."""
        data = after.copy()
        
        if entity_type == 'customer':
            data['dob'] = DataConverter.to_date(data.get('dob'))
        elif entity_type == 'product':
            data['price'] = DataConverter.to_float(data.get('price'))
        elif entity_type == 'order':
            data['discount'] = DataConverter.to_float(data.get('discount')) or 0.0
            raw_date = data.get('order_date')
            data['order_date'] = DataConverter.to_date(raw_date) if raw_date else datetime.now()
        elif entity_type == 'payment':
            data['amount'] = DataConverter.to_float(data.get('amount'))
            
        return data
