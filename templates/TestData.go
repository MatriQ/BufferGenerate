package Message

var TestData struct {
	id int
}

func (testData *TestData) GetID() int {
	return testData.id
}
func (testData *TestData) SetID(id int) {
	testData.id = id
}
