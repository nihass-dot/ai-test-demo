# --- AI-Generated Test ---
import pytest
from datetime import datetime, timezone
# Assuming the test file is in a 'tests' directory at the root,
# and the source file is in 'services/data_processor.py'
from services.data_processor import process_orders, find_high_value_orders

class TestDataProcessor:

    # --- Tests for process_orders function ---
    def test_process_orders_valid_data(self):
        raw_data = [
            {'id': '1', 'total_amount': '123.45', 'order_date': '2023-01-15T10:00:00'},
            {'id': '2', 'total_amount': '99.99', 'order_date': '2023-01-16T11:30:00Z'},
            {'id': '3', 'total_amount': 500.0, 'order_date': '2023-01-17'} # Missing time, should default to 00:00:00
        ]
        processed = process_orders(raw_data)

        assert len(processed) == 3
        assert processed[0]['id'] == '1'
        assert processed[0]['total_amount'] == 123.45
        assert isinstance(processed[0]['total_amount'], float)
        assert isinstance(processed[0]['order_date'], datetime)
        assert processed[0]['order_date'] == datetime(2023, 1, 15, 10, 0, 0)

        assert processed[1]['id'] == '2'
        assert processed[1]['total_amount'] == 99.99
        assert isinstance(processed[1]['total_amount'], float)
        assert isinstance(processed[1]['order_date'], datetime)
        # ISO format with 'Z' implies UTC
        assert processed[1]['order_date'] == datetime(2023, 1, 16, 11, 30, 0, tzinfo=timezone.utc)
        
        assert processed[2]['id'] == '3'
        assert processed[2]['total_amount'] == 500.0
        assert isinstance(processed[2]['total_amount'], float)
        assert isinstance(processed[2]['order_date'], datetime)
        assert processed[2]['order_date'] == datetime(2023, 1, 17, 0, 0, 0)

    def test_process_orders_empty_list(self):
        processed = process_orders([])
        assert len(processed) == 0

    def test_process_orders_missing_required_keys(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': '100.00'}, # Missing order_date
            {'order_date': '2023-01-01', 'total_amount': '50.00'}, # Missing id
            {'id': '3', 'order_date': '2023-01-03'} # Missing total_amount
        ]
        processed = process_orders(raw_data)
        assert len(processed) == 0
        captured = capsys.readouterr()
        assert "Skipping malformed order: 1" in captured.out
        assert "Skipping malformed order: None" in captured.out # For missing ID
        assert "Skipping malformed order: 3" in captured.out

    def test_process_orders_invalid_date_format(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': '100.00', 'order_date': 'not-a-date'},
            {'id': '2', 'total_amount': '50.00', 'order_date': '2023/01/01'} # Not ISO format
        ]
        processed = process_orders(raw_data)
        assert len(processed) == 0
        captured = capsys.readouterr()
        assert "Skipping order with invalid data: 1" in captured.out
        assert "Skipping order with invalid data: 2" in captured.out

    def test_process_orders_invalid_amount_format(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': 'abc', 'order_date': '2023-01-01'},
            {'id': '2', 'total_amount': None, 'order_date': '2023-01-02'},
            {'id': '3', 'total_amount': [], 'order_date': '2023-01-03'}
        ]
        processed = process_orders(raw_data)
        assert len(processed) == 0
        captured = capsys.readouterr()
        assert "Skipping order with invalid data: 1" in captured.out
        assert "Skipping order with invalid data: 2" in captured.out
        assert "Skipping order with invalid data: 3" in captured.out

    def test_process_orders_mixed_valid_and_invalid_data(self, capsys):
        raw_data = [
            {'id': '1', 'total_amount': '100.00', 'order_date': '2023-01-01T10:00:00'}, # Valid
            {'id': '2', 'total_amount': 'abc', 'order_date': '2023-01-02'},           # Invalid amount
            {'id': '3', 'total_amount': '200.00', 'order_date': 'bad-date'},           # Invalid date
            {'id': '4', 'total_amount': '300.00'},                                     # Missing order_date
            {'id': '5', 'total_amount': '50.50', 'order_date': '2023-01-05'}           # Valid
        ]
        processed = process_orders(raw_data)
        assert len(processed) == 2
        assert processed[0]['id'] == '1'
        assert processed[1]['id'] == '5'
        captured = capsys.readouterr()
        assert "Skipping order with invalid data: 2" in captured.out
        assert "Skipping order with invalid data: 3" in captured.out
        assert "Skipping malformed order: 4" in captured.out
        
    def test_process_orders_amount_as_int_string(self):
        raw_data = [
            {'id': '1', 'total_amount': '100', 'order_date': '2023-01-01'}
        ]
        processed = process_orders(raw_data)
        assert len(processed) == 1
        assert processed[0]['total_amount'] == 100.0
        assert isinstance(processed[0]['total_amount'], float)


    # --- Tests for find_high_value_orders function ---
    def test_find_high_value_orders_basic_filtering(self):
        orders = [
            {'id': '1', 'total_amount': 50.0},
            {'id': '2', 'total_amount': 150.0},
            {'id': '3', 'total_amount': 99.99},
            {'id': '4', 'total_amount': 200.0}
        ]
        high_value_orders = find_high_value_orders(orders, threshold=100.0)
        assert len(high_value_orders) == 2
        assert high_value_orders[0]['id'] == '2'
        assert high_value_orders[1]['id'] == '4'

    def test_find_high_value_orders_empty_list(self):
        high_value_orders = find_high_value_orders([])
        assert len(high_value_orders) == 0

    def test_find_high_value_orders_all_above_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 101.0},
            {'id': '2', 'total_amount': 200.0}
        ]
        high_value_orders = find_high_value_orders(orders, threshold=100.0)
        assert len(high_value_orders) == 2
        assert high_value_orders[0]['id'] == '1'
        assert high_value_orders[1]['id'] == '2'

    def test_find_high_value_orders_none_above_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 99.0},
            {'id': '2', 'total_amount': 50.0}
        ]
        high_value_orders = find_high_value_orders(orders, threshold=100.0)
        assert len(high_value_orders) == 0

    def test_find_high_value_orders_exact_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 100.0}, # Should not be included (not > 100)
            {'id': '2', 'total_amount': 100.01} # Should be included
        ]
        high_value_orders = find_high_value_orders(orders, threshold=100.0)
        assert len(high_value_orders) == 1
        assert high_value_orders[0]['id'] == '2'

    def test_find_high_value_orders_custom_threshold(self):
        orders = [
            {'id': '1', 'total_amount': 500.0},
            {'id': '2', 'total_amount': 700.0},
            {'id': '3', 'total_amount': 400.0}
        ]
        high_value_orders = find_high_value_orders(orders, threshold=600.0)
        assert len(high_value_orders) == 1
        assert high_value_orders[0]['id'] == '2'

    def test_find_high_value_orders_missing_total_amount_key(self):
        orders = [
            {'id': '1', 'total_amount': 150.0},
            {'id': '2', 'order_date': '2023-01-01'}, # Missing total_amount, defaults to 0
            {'id': '3', 'total_amount': 50.0}
        ]
        # Order '2' will have total_amount default to 0 (less than 100)
        high_value_orders = find_high_value_orders(orders, threshold=100.0)
        assert len(high_value_orders) == 1
        assert high_value_orders[0]['id'] == '1'

    def test_find_high_value_orders_non_list_input_raises_typeerror(self):
        with pytest.raises(TypeError, match="Input must be a list of orders."):
            find_high_value_orders("not a list")
        with pytest.raises(TypeError, match="Input must be a list of orders."):
            find_high_value_orders(None)
        with pytest.raises(TypeError, match="Input must be a list of orders."):
            find_high_value_orders({'id': '1', 'total_amount': 100.0})

# --- End AI-Generated Test ---
