# This file will be automatically filled by the AI.



# --- AI-Generated Test ---
import pytest
from datetime import datetime, timezone
from services.data_processor import process_orders, find_high_value_orders

# Helper function to create datetime objects for consistent assertions
def create_datetime_utc(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)

def create_datetime_naive(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    return datetime(year, month, day, hour, minute, second, microsecond)


class TestProcessOrders:

    def test_process_orders_valid_data_iso_with_and_without_tz(self):
        raw_data = [
            {'id': '1', 'total_amount': '150.75', 'order_date': '2023-01-01T10:00:00Z'},
            {'id': '2', 'total_amount': 99.99, 'order_date': '2023-01-02T11:30:00+00:00'},
            {'id': '3', 'total_amount': '25.0', 'order_date': '2023-01-03T12:00:00'} # Naive datetime
        ]
        expected_data = [
            {'id': '1', 'total_amount': 150.75, 'order_date': create_datetime_utc(2023, 1, 1, 10, 0, 0)},
            {'id': '2', 'total_amount': 99.99, 'order_date': create_datetime_utc(2023, 1, 2, 11, 30, 0)},
            {'id': '3', 'total_amount': 25.0, 'order_date': create_datetime_naive(2023, 1, 3, 12, 0, 0)}
        ]
        result = process_orders(raw_data)
        assert len(result) == len(expected_data)
        for i, order in enumerate(result):
            assert order['id'] == expected_data[i]['id']
            assert order['total_amount'] == pytest.approx(expected_data[i]['total_amount'])
            assert order['order_date'] == expected_data[i]['order_date']

    def test_process_orders_empty_input(self):
        result = process_orders([])
        assert result == []

    def test_process_orders_missing_required_keys(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': '100.00'}, # Missing order_date
            {'total_amount': '200.00', 'order_date': '2023-01-01T10:00:00Z'}, # Missing id
            {'id': '3', 'order_date': '2023-01-01T10:00:00Z'} # Missing total_amount
        ]
        result = process_orders(raw_data)
        assert result == []
        captured = capsys.readouterr()
        assert "Skipping malformed order: 1" in captured.out
        assert "Skipping malformed order: None" in captured.out # For missing 'id' key
        assert "Skipping malformed order: 3" in captured.out


    def test_process_orders_invalid_date_format(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': '100.00', 'order_date': 'invalid-date'},
            {'id': '2', 'total_amount': '200.00', 'order_date': '2023/01/01'} # Not ISO 8601
        ]
        result = process_orders(raw_data)
        assert result == []
        captured = capsys.readouterr()
        assert "Skipping order with invalid data: 1" in captured.out
        assert "Skipping order with invalid data: 2" in captured.out

    def test_process_orders_invalid_amount_type(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': 'abc', 'order_date': '2023-01-01T10:00:00Z'},
            {'id': '2', 'total_amount': None, 'order_date': '2023-01-01T10:00:00Z'} # TypeError from float(None)
        ]
        result = process_orders(raw_data)
        assert result == []
        captured = capsys.readouterr()
        assert "Skipping order with invalid data: 1" in captured.out
        assert "Skipping order with invalid data: 2" in captured.out

    def test_process_orders_mixed_valid_invalid(self):
        raw_data = [
            {'id': '1', 'total_amount': '150.75', 'order_date': '2023-01-01T10:00:00Z'}, # Valid
            {'id': '2', 'total_amount': 'invalid', 'order_date': '2023-01-02T11:00:00Z'}, # Invalid amount
            {'id': '3', 'order_date': '2023-01-03T12:00:00Z'}, # Missing total_amount
            {'id': '4', 'total_amount': '50.00', 'order_date': '2023-01-04T13:00:00Z'} # Valid
        ]
        expected_data = [
            {'id': '1', 'total_amount': 150.75, 'order_date': create_datetime_utc(2023, 1, 1, 10, 0, 0)},
            {'id': '4', 'total_amount': 50.00, 'order_date': create_datetime_utc(2023, 1, 4, 13, 0, 0)}
        ]
        result = process_orders(raw_data)
        assert len(result) == len(expected_data)
        # Check specific orders to ensure the correct ones were processed
        assert result[0]['id'] == '1'
        assert result[1]['id'] == '4'
        assert result[0]['total_amount'] == pytest.approx(150.75)
        assert result[1]['total_amount'] == pytest.approx(50.00)

    def test_process_orders_extra_keys_preserved(self):
        raw_data = [
            {'id': '1', 'total_amount': '100.00', 'order_date': '2023-01-01T10:00:00Z', 'customer_id': 'ABC', 'items': ['itemA', 'itemB']},
        ]
        result = process_orders(raw_data)
        assert len(result) == 1
        assert result[0]['customer_id'] == 'ABC'
        assert result[0]['items'] == ['itemA', 'itemB']

    def test_process_orders_total_amount_as_number(self):
        raw_data = [
            {'id': '1', 'total_amount': 100.50, 'order_date': '2023-01-01T10:00:00Z'}, # Already float
            {'id': '2', 'total_amount': 200, 'order_date': '2023-01-02T11:00:00Z'}, # Already int
        ]
        result = process_orders(raw_data)
        assert len(result) == 2
        assert result[0]['total_amount'] == pytest.approx(100.50)
        assert isinstance(result[0]['total_amount'], float)
        assert result[1]['total_amount'] == pytest.approx(200.00)
        assert isinstance(result[1]['total_amount'], float)

class TestFindHighValueOrders:

    def test_find_high_value_orders_basic(self):
        orders = [
            {'id': '1', 'total_amount': 150.0, 'order_date': create_datetime_utc(2023, 1, 1)},
            {'id': '2', 'total_amount': 99.99, 'order_date': create_datetime_utc(2023, 1, 2)},
            {'id': '3', 'total_amount': 200.0, 'order_date': create_datetime_utc(2023, 1, 3)},
            {'id': '4', 'total_amount': 50.0, 'order_date': create_datetime_utc(2023, 1, 4)},
        ]
        high_value_orders = find_high_value_orders(orders) # Default threshold 100.0
        assert len(high_value_orders) == 2
        assert high_value_orders[0]['id'] == '1'
        assert high_value_orders[1]['id'] == '3'

    def test_find_high_value_orders_custom_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 150.0, 'order_date': create_datetime_utc(2023, 1, 1)},
            {'id': '2', 'total_amount': 250.0, 'order_date': create_datetime_utc(2023, 1, 2)},
            {'id': '3', 'total_amount': 75.0, 'order_date': create_datetime_utc(2023, 1, 3)},
        ]
        high_value_orders = find_high_value_orders(orders, threshold=200.0)
        assert len(high_value_orders) == 1
        assert high_value_orders[0]['id'] == '2'

    def test_find_high_value_orders_empty_list(self):
        orders = []
        high_value_orders = find_high_value_orders(orders)
        assert high_value_orders == []

    def test_find_high_value_orders_all_below_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 50.0, 'order_date': create_datetime_utc(2023, 1, 1)},
            {'id': '2', 'total_amount': 75.0, 'order_date': create_datetime_utc(2023, 1, 2)},
        ]
        high_value_orders = find_high_value_orders(orders)
        assert high_value_orders == []

    def test_find_high_value_orders_all_above_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 150.0, 'order_date': create_datetime_utc(2023, 1, 1)},
            {'id': '2', 'total_amount': 200.0, 'order_date': create_datetime_utc(2023, 1, 2)},
        ]
        high_value_orders = find_high_value_orders(orders)
        assert len(high_value_orders) == 2
        assert high_value_orders[0]['id'] == '1'
        assert high_value_orders[1]['id'] == '2'

    def test_find_high_value_orders_at_threshold_exact_value(self):
        orders = [
            {'id': '1', 'total_amount': 100.0, 'order_date': create_datetime_utc(2023, 1, 1)}, # Exactly 100
            {'id': '2', 'total_amount': 100.01, 'order_date': create_datetime_utc(2023, 1, 2)}, # Just above 100
        ]
        high_value_orders = find_high_value_orders(orders)
        assert len(high_value_orders) == 1
        assert high_value_orders[0]['id'] == '2'

    def test_find_high_value_orders_missing_amount_key(self):
        orders = [
            {'id': '1', 'total_amount': 150.0, 'order_date': create_datetime_utc(2023, 1, 1)},
            {'id': '2', 'order_date': create_datetime_utc(2023, 1, 2)}, # Missing total_amount (defaults to 0 for comparison)
            {'id': '3', 'total_amount': 200.0, 'order_date': create_datetime_utc(2023, 1, 3)},
        ]
        high_value_orders = find_high_value_orders(orders)
        assert len(high_value_orders) == 2
        assert high_value_orders[0]['id'] == '1'
        assert high_value_orders[1]['id'] == '3'

    def test_find_high_value_orders_non_list_input_raises_type_error(self):
        with pytest.raises(TypeError, match="Input must be a list of orders."):
            find_high_value_orders("not a list")
        with pytest.raises(TypeError, match="Input must be a list of orders."):
            find_high_value_orders(None)
        with pytest.raises(TypeError, match="Input must be a list of orders."):
            find_high_value_orders(123)

# --- End AI-Generated Test ---
