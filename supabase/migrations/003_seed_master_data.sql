-- Production master data only. No demo customers, bookings or payments.

insert into public.ceremony_types (name_tamil, name_english, description, default_duration_minutes, is_active)
select * from (values
 ('திருமணம்','Marriage','திருமண வைதீக சடங்கு',180,true),
 ('கிரகப்பிரவேசம்','Griha Pravesam','புது வீடு புகும் சடங்கு',150,true),
 ('கணபதி ஹோமம்','Ganapathi Homam','விநாயகர் ஹோமம்',120,true),
 ('ஆயுஷ் ஹோமம்','Ayush Homam','ஆயுள் ஆரோக்கிய ஹோமம்',120,true),
 ('நாமகரணம்','Naming Ceremony','குழந்தை பெயரிடும் சடங்கு',90,true),
 ('நிச்சயதார்த்தம்','Engagement','திருமண நிச்சய சடங்கு',90,true),
 ('சீமந்தம்','Seemantham','மங்கள சடங்கு',120,true),
 ('உபநயனம்','Upanayanam','பூணூல் சடங்கு',180,true)
) v(name_tamil,name_english,description,default_duration_minutes,is_active)
where not exists (
  select 1 from public.ceremony_types c where c.name_english = v.name_english
);

insert into public.pooja_templates (ceremony_type_id, name)
select c.id, c.name_tamil || ' - பொதுப் பட்டியல்'
from public.ceremony_types c
where not exists (
  select 1 from public.pooja_templates t where t.ceremony_type_id = c.id
);

with items(ceremony_english,item_name_tamil,item_name_english,quantity,unit,mandatory,sort_order) as (values
 ('Marriage','தேங்காய்','Coconut',5::numeric,'எண்',true,1),
 ('Marriage','மஞ்சள்','Turmeric',1::numeric,'பொதி',true,2),
 ('Marriage','குங்குமம்','Kumkum',1::numeric,'பொதி',true,3),
 ('Marriage','வெற்றிலை','Betel leaves',25::numeric,'இலை',true,4),
 ('Marriage','பாக்கு','Betel nuts',25::numeric,'எண்',true,5),
 ('Marriage','பழங்கள்','Fruits',1::numeric,'தட்டு',true,6),
 ('Marriage','மலர்கள்','Flowers',1::numeric,'தொகுப்பு',true,7),
 ('Marriage','அட்சதை','Akshathai',1::numeric,'பொதி',true,8),
 ('Griha Pravesam','தேங்காய்','Coconut',5::numeric,'எண்',true,1),
 ('Griha Pravesam','மஞ்சள்','Turmeric',1::numeric,'பொதி',true,2),
 ('Griha Pravesam','குங்குமம்','Kumkum',1::numeric,'பொதி',true,3),
 ('Griha Pravesam','மாமர இலை','Mango leaves',1::numeric,'தொகுப்பு',true,4),
 ('Griha Pravesam','கலசம்','Kalasam',1::numeric,'எண்',true,5),
 ('Griha Pravesam','அரிசி','Rice',2::numeric,'கிலோ',true,6),
 ('Griha Pravesam','நெய்','Ghee',1::numeric,'பாட்டில்',true,7),
 ('Griha Pravesam','ஹோமப் பொருட்கள்','Homam materials',1::numeric,'தொகுப்பு',true,8),
 ('Ganapathi Homam','தேங்காய்','Coconut',3::numeric,'எண்',true,1),
 ('Ganapathi Homam','அருகம்புல்','Arugampul',1::numeric,'தொகுப்பு',true,2),
 ('Ganapathi Homam','வாழைப்பழம்','Banana',12::numeric,'எண்',true,3),
 ('Ganapathi Homam','மலர்கள்','Flowers',1::numeric,'தொகுப்பு',true,4),
 ('Ganapathi Homam','நெய்','Ghee',1::numeric,'பாட்டில்',true,5),
 ('Ganapathi Homam','ஹோமப் பொருட்கள்','Homam materials',1::numeric,'தொகுப்பு',true,6),
 ('Ayush Homam','கலசம்','Kalasam',1::numeric,'எண்',true,1),
 ('Ayush Homam','நெய்','Ghee',1::numeric,'பாட்டில்',true,2),
 ('Ayush Homam','ஹோமப் பொருட்கள்','Homam materials',1::numeric,'தொகுப்பு',true,3),
 ('Ayush Homam','பழங்கள்','Fruits',1::numeric,'தட்டு',true,4),
 ('Ayush Homam','மலர்கள்','Flowers',1::numeric,'தொகுப்பு',true,5),
 ('Naming Ceremony','மஞ்சள்','Turmeric',1::numeric,'பொதி',true,1),
 ('Naming Ceremony','குங்குமம்','Kumkum',1::numeric,'பொதி',true,2),
 ('Naming Ceremony','பழங்கள்','Fruits',1::numeric,'தட்டு',true,3),
 ('Naming Ceremony','மலர்கள்','Flowers',1::numeric,'தொகுப்பு',true,4),
 ('Naming Ceremony','வெற்றிலை','Betel leaves',15::numeric,'இலை',true,5),
 ('Naming Ceremony','பாக்கு','Betel nuts',15::numeric,'எண்',true,6),
 ('Engagement','தேங்காய்','Coconut',3::numeric,'எண்',true,1),
 ('Engagement','மஞ்சள்','Turmeric',1::numeric,'பொதி',true,2),
 ('Engagement','குங்குமம்','Kumkum',1::numeric,'பொதி',true,3),
 ('Engagement','வெற்றிலை','Betel leaves',25::numeric,'இலை',true,4),
 ('Engagement','பாக்கு','Betel nuts',25::numeric,'எண்',true,5),
 ('Engagement','மலர்கள்','Flowers',1::numeric,'தொகுப்பு',true,6),
 ('Engagement','பழங்கள்','Fruits',1::numeric,'தட்டு',true,7)
)
insert into public.pooja_items (
  template_id,item_name_tamil,item_name_english,quantity,unit,mandatory,sort_order
)
select t.id,i.item_name_tamil,i.item_name_english,i.quantity,i.unit,i.mandatory,i.sort_order
from items i
join public.ceremony_types c on c.name_english=i.ceremony_english
join public.pooja_templates t on t.ceremony_type_id=c.id
where not exists (
  select 1 from public.pooja_items p
  where p.template_id=t.id and p.item_name_tamil=i.item_name_tamil
);
