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

/**
 * Разрешённые поля формы; идентификатор и связи задаются сервером.
 */
public class PetForm {

	private final Pet value;

	public PetForm(Pet value) {
		this.value = value;
	}

	public Integer getId() {
		return this.value.getId();
	}

	public boolean isNew() {
		return this.value.isNew();
	}

	public String getName() {
		return this.value.getName();
	}

	public void setName(String name) {
		this.value.setName(name);
	}

	@DateTimeFormat(pattern = "yyyy-MM-dd")
	public LocalDate getBirthDate() {
		return this.value.getBirthDate();
	}

	public void setBirthDate(LocalDate birthDate) {
		this.value.setBirthDate(birthDate);
	}

	public PetType getType() {
		return this.value.getType();
	}

	public void setType(PetType type) {
		this.value.setType(type);
	}

	Pet toPet() {
		return this.value;
	}

}
