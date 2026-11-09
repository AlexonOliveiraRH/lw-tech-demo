package com.acme.orders;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.thoughtworks.xstream.XStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericDatumReader;
import org.apache.avro.generic.GenericDatumWriter;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.io.BinaryEncoder;
import org.apache.avro.io.DecoderFactory;
import org.apache.avro.io.EncoderFactory;
import org.apache.commons.beanutils.BeanUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.expression.Expression;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.web.util.UriComponentsBuilder;

/**
 * Order workflow touching each library of the Lightwell Java Remediated set.
 * The code is identical on public Maven Central builds and on Lightwell builds.
 */
public class OrderService {

    private static final Logger LOG = LoggerFactory.getLogger(OrderService.class);

    static final Schema ORDER_SCHEMA = new Schema.Parser().parse(
            "{\"type\":\"record\",\"name\":\"Order\",\"namespace\":\"com.acme.orders\",\"fields\":["
                    + "{\"name\":\"id\",\"type\":\"string\"},"
                    + "{\"name\":\"customer\",\"type\":\"string\"},"
                    + "{\"name\":\"country\",\"type\":\"string\"},"
                    + "{\"name\":\"amount\",\"type\":\"double\"}]}");

    private final ObjectMapper json = new ObjectMapper();
    private final XStream xml;
    private final Expression discountRule;

    public OrderService(String discountRule) {
        this.discountRule = new SpelExpressionParser().parseExpression(discountRule);
        this.xml = new XStream();
        this.xml.allowTypes(new Class<?>[] {Order.class});
        this.xml.alias("order", Order.class);
    }

    /** jackson-databind */
    public Order parse(String payload) {
        try {
            Order order = json.readValue(payload, Order.class);
            LOG.info("Parsed order {} for {}", order.getId(), order.getCustomer());
            return order;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    /** spring-expression (SpEL) */
    public double discount(Order order) {
        Double value = discountRule.getValue(order, Double.class);
        return value == null ? 0.0 : value;
    }

    /** commons-beanutils */
    public OrderSummary summarize(Order order) {
        OrderSummary summary = new OrderSummary();
        try {
            BeanUtils.copyProperties(summary, order);
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException(e);
        }
        return summary;
    }

    /** xstream */
    public String toXml(Order order) {
        return xml.toXML(order);
    }

    public Order fromXml(String document) {
        return (Order) xml.fromXML(document);
    }

    /** avro */
    public byte[] toAvro(Order order) {
        GenericRecord record = new GenericData.Record(ORDER_SCHEMA);
        record.put("id", order.getId());
        record.put("customer", order.getCustomer());
        record.put("country", order.getCountry());
        record.put("amount", order.getAmount());
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        BinaryEncoder encoder = EncoderFactory.get().binaryEncoder(out, null);
        try {
            new GenericDatumWriter<GenericRecord>(ORDER_SCHEMA).write(record, encoder);
            encoder.flush();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return out.toByteArray();
    }

    public GenericRecord fromAvro(byte[] bytes) {
        try {
            return new GenericDatumReader<GenericRecord>(ORDER_SCHEMA)
                    .read(null, DecoderFactory.get().binaryDecoder(bytes, null));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    /** spring-web */
    public String trackingUrl(Order order) {
        return UriComponentsBuilder.fromHttpUrl("https://orders.acme.example/track")
                .queryParam("id", order.getId())
                .queryParam("country", order.getCountry())
                .toUriString();
    }

    /** spring-security-core */
    public String requiredAuthority(Order order) {
        String role = order.getAmount() >= 1000 ? "ROLE_ORDER_APPROVER" : "ROLE_ORDER_CLERK";
        return new SimpleGrantedAuthority(role).getAuthority();
    }
}
