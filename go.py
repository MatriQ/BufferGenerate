package $PACKAGENAME$

var $CLASSNAME$ struct {
<for $item in $Fields$>	
	$item.$FieldsName $item.$FieldsType
	/*_ID        int32
	_age       int16
	_sex       bool
	_Name      string
	_Friends    []*int32
	_FriendData *FriendData
	_Datas      []FriendData*/
<endfor>
}

func (_TestMessage *TestMessage) GetID() int32 {
	return _TestMessage.ID
}
func (_TestMessage *TestMessage) SetID(_ID int32) {
	_TestMessage.ID = _ID
}

func (_TestMessage *TestMessage) Getage() int16 {
	return _TestMessage.age
}
func (_TestMessage *TestMessage) Setage(_age int16) {
	_TestMessage.age = _age
}
func (_TestMessage *TestMessage) Getsex() bool {
	return _TestMessage.sex
}
func (_TestMessage *TestMessage) Setsex(_sex bool) {
	_TestMessage.sex = _sex
}
func (_TestMessage *TestMessage) GetName() string {
	return _TestMessage.Name
}
func (_TestMessage *TestMessage) SetID(_Name string) {
	_TestMessage.Name = _Name
}
func (_TestMessage *TestMessage) GetFriends() []int32 {
	return _TestMessage.Friends
}
func (_TestMessage *TestMessage) SetID(_Friends []int32) {
	_TestMessage.Friends = _Friends
}
func (_TestMessage *TestMessage) GetFriendData() *FriendData {
	return _TestMessage.FriendData
}
func (_TestMessage *TestMessage) SetID(_FriendData *FriendData) {
	_TestMessage.FriendData = _FriendData
}
func (_TestMessage *TestMessage) GetDatas() []*FriendData {
	return _TestMessage.Datas
}
func (_TestMessage *TestMessage) SetDatas(_Datas []*FriendData) {
	_TestMessage.Datas = _ID
}
