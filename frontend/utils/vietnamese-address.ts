export interface WardOption {
  name: string
}

export interface DistrictOption {
  name: string
  wards: WardOption[]
}

export interface ProvinceOption {
  name: string
  districts: DistrictOption[]
}

export const vietnameseAddresses: ProvinceOption[] = [
  {
    name: 'TP. Hồ Chí Minh',
    districts: [
      {
        name: 'Quan 1',
        wards: [
          { name: 'Phuong Ben Thanh' },
          { name: 'Phuong Da Kao' },
          { name: 'Phuong Tan Dinh' },
        ],
      },
      {
        name: 'Quan 3',
        wards: [{ name: 'Phuong Vo Thi Sau' }, { name: 'Phuong 9' }, { name: 'Phuong 12' }],
      },
      {
        name: 'Quan 7',
        wards: [{ name: 'Phuong Tan Phu' }, { name: 'Phuong Tan Quy' }, { name: 'Phuong Phu My' }],
      },
      {
        name: 'Thu Duc',
        wards: [
          { name: 'Phuong Linh Trung' },
          { name: 'Phuong Thao Dien' },
          { name: 'Phuong Hiep Binh Chanh' },
        ],
      },
    ],
  },
  {
    name: 'Dong Nai',
    districts: [
      {
        name: 'Bien Hoa',
        wards: [{ name: 'Phuong Tan Phong' }, { name: 'Phuong Long Binh' }],
      },
    ],
  },
]

export function getDistricts(city: string): DistrictOption[] {
  return vietnameseAddresses.find((province) => province.name === city)?.districts ?? []
}

export function getWards(city: string, district: string): WardOption[] {
  return getDistricts(city).find((item) => item.name === district)?.wards ?? []
}
