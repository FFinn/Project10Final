/*
 * Copyright 2012-2025 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.owner;

import java.time.LocalDate;
import org.springframework.format.annotation.DateTimeFormat;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Разрешённые поля формы; идентификатор и связи задаются сервером.
 */
public class VisitForm {

	private final Visit value;

	public VisitForm(Visit value) {
		this.value = value;
	}

	public Integer getId() {
		return this.value.getId();
	}

	public boolean isNew() {
		return this.value.isNew();
	}

	@DateTimeFormat(pattern = "yyyy-MM-dd")
	public LocalDate getDate() {
		return this.value.getDate();
	}

	public void setDate(LocalDate date) {
		this.value.setDate(date);
	}

	@NotBlank
	@Size(max = 255)
	public String getDescription() {
		return this.value.getDescription();
	}

	public void setDescription(String description) {
		this.value.setDescription(description);
	}

	Visit toVisit() {
		return this.value;
	}

}
