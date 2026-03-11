-- Trigger for Customer Updates
DROP TRIGGER IF EXISTS trg_customer_audit;
-- split
CREATE TRIGGER trg_customer_audit
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    IF OLD.email <> NEW.email THEN
        INSERT INTO ecommerce_audit (entity_type, entity_id, attribute_changed, old_value, new_value, changed_by)
        VALUES ('customer', NEW.cid, 'email', OLD.email, NEW.email, USER());
    END IF;
    IF OLD.address <> NEW.address THEN
        INSERT INTO ecommerce_audit (entity_type, entity_id, attribute_changed, old_value, new_value, changed_by)
        VALUES ('customer', NEW.cid, 'address', OLD.address, NEW.address, USER());
    END IF;
END;
-- split

-- Trigger for Order/Status Changes
DROP TRIGGER IF EXISTS trg_order_status_audit;
-- split
CREATE TRIGGER trg_order_status_audit
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    IF OLD.payment_status <> NEW.payment_status THEN
        INSERT INTO ecommerce_audit (entity_type, entity_id, attribute_changed, old_value, new_value, changed_by)
        VALUES ('payment', NEW.oid, 'payment_status', OLD.payment_status, NEW.payment_status, USER());
    END IF;
END;

