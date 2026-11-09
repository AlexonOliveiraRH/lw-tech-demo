package com.acme.orders;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.apache.avro.generic.GenericRecord;
import org.junit.jupiter.api.Test;
import org.springframework.context.ConfigurableApplicationContext;

/** Behavioral tests: the contract stays green on public and Lightwell (rhlw) builds. */
class OrderServiceTest {

    private final OrderService service = new OrderService("amount > 100 ? amount * 0.1 : 0.0");
    private final Order order = new Order("A-1001", "Initech", "BR", 250.0);

    @Test
    void parsesJson() {
        Order parsed = service.parse(
                "{\"id\":\"A-1001\",\"customer\":\"Initech\",\"country\":\"BR\",\"amount\":250.0}");
        assertEquals("Initech", parsed.getCustomer());
        assertEquals(250.0, parsed.getAmount());
    }

    @Test
    void appliesDiscountRule() {
        assertEquals(25.0, service.discount(order), 0.0001);
        assertEquals(0.0, service.discount(new Order("A-1", "Hooli", "US", 50.0)), 0.0001);
    }

    @Test
    void copiesSummary() {
        OrderSummary summary = service.summarize(order);
        assertEquals("A-1001", summary.getId());
        assertEquals(250.0, summary.getAmount());
    }

    @Test
    void roundTripsXml() {
        String xml = service.toXml(order);
        assertTrue(xml.startsWith("<order>"));
        assertEquals("Initech", service.fromXml(xml).getCustomer());
    }

    @Test
    void roundTripsAvro() {
        GenericRecord record = service.fromAvro(service.toAvro(order));
        assertEquals("A-1001", record.get("id").toString());
        assertEquals(250.0, (Double) record.get("amount"), 0.0001);
    }

    @Test
    void buildsTrackingUrlAndAuthority() {
        assertEquals("https://orders.acme.example/track?id=A-1001&country=BR", service.trackingUrl(order));
        assertEquals("ROLE_ORDER_CLERK", service.requiredAuthority(order));
    }

    @Test
    void springContextStarts() {
        try (ConfigurableApplicationContext ctx = OrdersApplication.start()) {
            assertEquals(25.0, ctx.getBean(OrderService.class).discount(order), 0.0001);
        }
    }
}
