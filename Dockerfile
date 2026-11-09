FROM maven:3.9-eclipse-temurin-21@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320 AS build
WORKDIR /build
COPY pom.xml ./
COPY .mvn .mvn
COPY src src
RUN mvn -B -ntp -DskipTests package

FROM eclipse-temurin:21-jre-alpine@sha256:ac05c3c42b7c2f1a52c9bd52f01041fa1958231b15ebeae7420429cbc5baf474 AS runtime
RUN apk add --no-cache zlib=1.4-r0 \
    && addgroup -g 10001 app \
    && adduser -D -H -u 10001 -G app app
WORKDIR /app
COPY --from=build --chown=10001:10001 /build/target/*.jar /app/petclinic.jar
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/actuator/health"]
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=70", "-Djava.io.tmpdir=/tmp", "-jar", "/app/petclinic.jar"]
